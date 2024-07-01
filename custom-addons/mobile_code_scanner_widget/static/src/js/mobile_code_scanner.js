/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
// import ajax from 'web.ajax';
import { loadJS } from "@web/core/assets";
import { CharField,charField } from "@web/views/fields/char/char_field";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc_service";
const { useRef, onWillStart } = owl;

export class MobileCodeScannerWidget extends CharField {
    static template = 'mobile_code_scanner_widget.MobileCodeScannerWidget';
    

    static props = {
        ...CharField.props,
       scanner_options: { type: Object, optional: true },
    };

    setup() {
        super.setup();
        this.videoRef = useRef('video');
        this.canvasRef = useRef('canvas');
        this.button = useRef('button')
        this.stop_button = useRef('stop_button')
        this.barcode_result = false
        this.input = useRef('input')
        this.rpc = useService("rpc");
        this.barcode_found = false
        this.captured_images = []
        this.image_elem = useRef('image_elem')
        this.scanned_imgs_count = 0
        this.flashlight_status = this.props.scanner_options.enable_flashlight_default || false
        this.enable_sound = this.props.scanner_options.enable_sound || false
        this.enable_backend_scan = this.props.scanner_options.enable_backend_scan || false
        this.flashlight_button = useRef('flashlight_btn')
        this.max_imgs_count = this.props.scanner_options.max_frames || 10
        // this.process_on_backend = this.props.options.process_on_backend || false
        onWillStart(() => {
            loadJS("/mobile_code_scanner_widget/static/src/js/lib/zxing-browser.min.js")
        })
    }

    //Due to browser standards, we cannot get the available input devices using enumerateDevices
    //before calling getUserMedia. So _setupWebcam method request camera permissions and then 
    //the _setCameraId method retrieves the available camera devices and stores the primary
    //back camera Id in the browser's localStorage to avoid requesting the deviceId each time the user wants
    //to scan.

    async _setupWebcam() {
        console.log("props",this.props)
        if (!localStorage.getItem('barcode_camera_id')) {
            var self = this

            const video = self.videoRef.el;
            const button = self.button.el
            const stop_button = self.stop_button.el
            video.style.display = ''
            button.style.display = 'none'
            stop_button.style.display = ''
            await navigator.mediaDevices.getUserMedia({ audio: false, video: true })
                .then(function (stream) {
                    video.srcObject = stream;
                    return video.play()
                })
                .catch(err => console.log(err))
        }

    }

    async _setCameraId() {
        var self = this
        await navigator.mediaDevices.enumerateDevices()
            .then((devices) => {
                var cameras = devices.filter(device => device.kind == "videoinput" && ((device.label.includes("back") && device.label.includes("0")))); //filter only back cameras
                if (cameras.length === 0) { //if no back cams are found, get use any of the available videoinputs
                    cameras = devices.filter(device => device.kind == "videoinput")
                }
                localStorage.setItem('barcode_camera_id', cameras[0].deviceId)
                self._removeVideoStreams()
            })
            .catch((err) => {
                console.log(err)
            })
    }

    async _removeVideoStreams() {
        const video = this.videoRef.el
        if (video.srcObject) {
            video.srcObject.getVideoTracks().forEach(track => {
                track.stop()
                video.srcObject.removeTrack(track);
            });
        }
    }

    async _startCamera() {
        var self = this
        self._showCaptureElements()
        if (!localStorage.getItem('barcode_camera_id')) {
            console.log("Camera is not set up!")
        }
        else {
            var camera_id = localStorage.getItem('barcode_camera_id')
            navigator.mediaDevices.getUserMedia({
                video: {
                    width: 600,
                    height: 600,
                    deviceId: camera_id,
                },
                audio: false
            })
                .then(function (stream) {
                    video.srcObject = stream;
                    video.play().then(res => {
                        self._toggleFlashLight().then(res2 => {
                            self._scanCode()
                        })
                    }).catch(err => console.log(err));
                })
                .catch(function (err) {
                    console.log("An error occurred: " + err);
                    return err
                });
        }
    }

    async _stopCapture() {
        var self = this
        self.barcode_found = true
        self._removeVideoStreams()
        self._hideCaptureElements()
        self.flashlight_status = !self.flashlight_status
    }

    async _scanCode() {
        var self = this
        if (self.scanned_imgs_count >= self.max_imgs_count) {
            self._stopCapture().then(res => {

                setTimeout(() => {
                    alert("Cannot find any barcodes!")

                }, 500)
            })
        }
        else if (!self.barcode_found) {
            const canvas = self.canvasRef.el;
            const video = self.videoRef.el;
            var context = canvas.getContext('2d');
            context.clearRect(0, 0, 600, 600);
            context.drawImage(video, 0, 0, 600, 600);
            self.image_elem.el.src = canvas.toDataURL('image/png');
            const codeReader = new ZXingBrowser.BrowserMultiFormatOneDReader();
            const reader = codeReader.decodeFromImageElement(self.image_elem.el)
                .then(res => {
                    self.barcode_found = true;
                    self.input.el.value = res.text
                    self.input.el.dispatchEvent(new Event('input', { bubbles: true }))
                    if(self.enable_sound)
                        {
                            self._playBeepSound()
                        }
                    self._stopCapture()
                }
                )
                .catch(
                    err => {
                        if (self.enable_backend_scan){
                            jsonrpc('/code_scanner/scan', {
                                image_data: self.image_elem.el.src.split(',')[1]
                            }, { 'async': false }).then(function (result) {
                                if (result.status === 'success') {
                                    self.barcode_found = true;
                                    self.input.el.value = result.scanned_code
                                    self.input.el.dispatchEvent(new Event('input', { bubbles: true }))
                                    if(self.enable_sound)
                                        {
                                            self._playBeepSound()
                                        }
                                    self._stopCapture()
                                } else {
                                    setTimeout(() => {
                                        self.scanned_imgs_count += 1
                                        self._scanCode()
    
                                    }, 500)
                                    console.log("Unable to find a barcode");
                                }
                            }).catch(function (error) {
                                console.log(error)
                            })
                        }
                        else{
                            setTimeout(() => {
                                self.scanned_imgs_count += 1
                                self._scanCode()

                            }, 500)
                        } 
                    }
                )
        }
    }

    async _hideCaptureElements() {
        this.videoRef.el.style.display = 'none'
        this.canvasRef.el.style.display = 'none'
        this.button.el.style.display = ''
        this.stop_button.el.style.display = 'none'
        this.flashlight_button.el.style.display = 'none'
    }

    async _showCaptureElements() {
        this.videoRef.el.style.display = ''
        this.button.el.style.display = 'none'
        this.stop_button.el.style.display = ''
        this.flashlight_button.el.style.display = ''

    }

    async _toggleFlashLight() {
        const video = this.videoRef.el
        var self = this
        if (video.srcObject) {
            var track = video.srcObject.getVideoTracks()[0]
            console.log(track)
            track.applyConstraints({
                advanced: [{
                    torch: self.flashlight_status,
                    // focusMode: 'continuous', 
                }]
            }).then(res => {
                if (self.flashlight_status === true) {
                    self.flashlight_button.el.style.backgroundColor = 'yellow'
                }
                else {
                    self.flashlight_button.el.style.backgroundColor = 'IndianRed'
                }
                self.flashlight_status = !self.flashlight_status

            }).catch(err => {
                self.flashlight_button.el.style.backgroundColor = 'IndianRed';
                console.log(err);

            });
        }
        else {
            console.log("No Video.srcObject")
        }
        return track
    }

    _playBeepSound() {
        var mp3_url = 'https://media.geeksforgeeks.org/wp-content/uploads/20190531135120/beep.mp3';
        (new Audio(mp3_url)).play()
    }

    async _onCapture(ev) {
        var self = this
        console.log(self.scanner_options)
        self.barcode_found = false
        self.scanned_imgs_count = 0
        await self._setupWebcam()
        self._setCameraId().then(res2 => {
            self._startCamera()
        }).catch(err => console.log(err))
    }
}
// MobileCodeScannerWidget.displayName = _lt("Code Scanner");
// MobileCodeScannerWidget.props = {
//     ...CharField.props,
//     options: { type: Object, optional: true },
// }
// MobileCodeScannerWidget.extractProps = ({ attrs, field }) => {
//     return {
//         options: attrs.options,
//     };
// };

export const MobileCodeScanner = {
    ...charField,
    component: MobileCodeScannerWidget,
    displayName: _t("Mobile Code Scanner"),
    supportedTypes: ["char"],
    extractProps: ({attrs, options}) => {
        var props = charField.extractProps({attrs,options})
        if(attrs.scanner_options){
            attrs.scanner_options = attrs.scanner_options.replace(/'/g, '"') || "{}"
        }
        else{
            attrs.scanner_options = "{}"
        }
        
        return{
            ...props,
            scanner_options: JSON.parse(attrs.scanner_options)

        }
    }
};


registry.category("fields").add("mobile_code_scanner", MobileCodeScanner);
