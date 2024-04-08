from functools import cache, lru_cache
import queue
import streamlit as st
import qrcode, requests, av, cv2, torch, numpy, threading, serial, time
from streamlit_lottie import st_lottie
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from numpy import random
from models.experimental import attempt_load
from utils.datasets import letterbox
from models.experimental import attempt_load
from utils.torch_utils import time_synchronized, TracedModel
from utils.plots import plot_one_box
from utils.general import non_max_suppression, check_img_size 
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# @cache
# Load the pre-trained model
# @lru_cache(maxsize=None)  # Cache the loaded model
def load_model():
    return attempt_load("weights/best.pt")

model = load_model()
def detect(img):

    img0 = img
    img = letterbox(img)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = numpy.ascontiguousarray(img)

    device = "cpu"
    img = torch.from_numpy(img).to(device)
    img = img.float()  # uint8 to fp16/32
    img /= 255.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    t1 = time_synchronized()
    with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
        pred = model(img)[0]
    t2 = time_synchronized()
    
    # Apply NMS
    pred = non_max_suppression(pred)
    t3 = time_synchronized()

    # model = TracedModel(model, device, 640)
    # names = model.module.names if hasattr(model, 'module') else model.names
    names = ['Glass', 'Metal', 'Paper', 'Plastic', 'GW']
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    s, res = '', ''
    for i, det in enumerate(pred):
        
        for c in det[:, -1].unique():
            n = (det[:, -1] == c).sum()  # detections per class
            s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
            
        
        if len (det):
            for *xyxy, conf, cls in reversed(det):
                label = f'{names[int(cls)]} {conf:.2f}'
                res = label
                plot_one_box(xyxy, img0, label=label, color=colors[int(cls)], line_thickness=1)
        
        # print (s) 
    
    return [img0, res]

# download lottie
# st.experimental_memo
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def inBin(port):
    ser = serial.Serial(port, 9600, timeout=1)
    t_end = time.time() + 10
    while time.time() < t_end:
        if ser.readline() == b'IR sensor detected an obstacle or reflective surface.\r\n':
            print("detected")
            ser.close()
            return True

    ser.close()
    return False


# Set the overall container width
st.markdown("""
    <style>
    .full-width {
        max-width: 100vw;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

def reset_user_session(s):
    st.session_state["_session"] = s
    print('session_state change',s)
    # st.experimental_rerun()

# Standby Screen

# random video display when there is no activity + instructions

# show item being scanned by the camera

# show which bin is appropriate * 4/5 bins with only one enlarged and bolded

# title

def binscreen(bin_number = 0):
    st.markdown("""
        <style>
        #root, .withScreencast {
            max-width: 100vw;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create columns with a percentage width
    col1, col2, col3, col4 = st.columns(4, )

    def __():
        pass

    with col1:
        st.image(
            caption="Plastic",
            image="https://images.pexels.com/photos/4887152/pexels-photo-4887152.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            
        )
        if bin_number == 0:
            st.image(caption="throw here", image="https://img.kingfisherdirect.co.uk/media/catalog/product/L/E/LEALIENBUDDY_3_spacebuddy-alien-recycling-bin-84-litre.jpg?width=600&height=600&store=kingfisherdirect&image-type=image")


    with col2:
        st.image(
            caption="Metal",
            image="https://images.pexels.com/photos/51320/drill-milling-milling-machine-drilling-51320.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
        )
        if bin_number == 1:
            st.image(caption="throw here", image="https://img.kingfisherdirect.co.uk/media/catalog/product/L/E/LEALIENBUDDY_3_spacebuddy-alien-recycling-bin-84-litre.jpg?width=600&height=600&store=kingfisherdirect&image-type=image")


    with col3:
        st.image(
            caption="Paper",
            image="https://images.pexels.com/photos/167538/pexels-photo-167538.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
        )
        if bin_number == 2:
            st.image(caption="throw here", image="https://img.kingfisherdirect.co.uk/media/catalog/product/L/E/LEALIENBUDDY_3_spacebuddy-alien-recycling-bin-84-litre.jpg?width=600&height=600&store=kingfisherdirect&image-type=image")


    with col4:
        st.image(
            caption="Glass",
            image="https://images.pexels.com/photos/1148450/pexels-photo-1148450.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
        )
        if bin_number == 3:
            st.image(caption="throw here", image="https://img.kingfisherdirect.co.uk/media/catalog/product/L/E/LEALIENBUDDY_3_spacebuddy-alien-recycling-bin-84-litre.jpg?width=600&height=600&store=kingfisherdirect&image-type=image")

    flag = True #inBin("COM8")
    nextpage = "None"
    if flag:
        reset_user_session("qr")
        st.write("object detected")
        # main()
        nextpage = "qr"
    else:
        reset_user_session("None")
        st.write("object detected")
    
    st.button("next", on_click=main)
    components.html ("""<script>
            const bt = window.parent.document.querySelectorAll('.stButton > Button');
                
            for (var i = 0; i < bt.length; i++) {
            bt[i].click(); // Click each button
            bt[i].style.display = "none";
            }
            console.log("done");
            </script>""")

# show QR code and appreciation

# Function to generate and display QR code
def generate_qr_code(data, size=200):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").resize((size, size))
    st.sidebar.image(img, caption="Scan this QR Code", use_column_width=True)

def qrscreen():
    st.sidebar.write("Scan this QR Code to claim your points:")
    score = "30"
    binID = "1"
    # key has to be the primary id of the transaction => unique 
    key = ""

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("smartbin-c09bd-firebase-adminsdk-9k368-b97ae8a87a.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL':"https://smartbin-c09bd-default-rtdb.europe-west1.firebasedatabase.app/"
                })
        ref = db.reference("")
        data = {
            "username": "default_value",
            "datatime": time.time(),
            "binID": binID,
            "score": score
        }
        t = ref.child("transactions").push(data)
        key = t.key
    except:
        st.warning("Error with db.")
    # then with this key & score we create a transaction with out user name
    # _url = f"http://192.168.39.149:8502/?key={key}"
    _url = f"http://192.168.39.149:8502/?key={key}"
    generate_qr_code(_url)
    
    # st.markdown("<h4 sytle= \"color:green\">Thank you for saving the environment</h4>", unsafe_allow_html=True)
    lottie_url = "https://lottie.host/9b54e103-a286-4296-95dd-6ddded2536a0/2KnPT6hpSU.json"
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, height=600)
    
    
    time.sleep(15)
    reset_user_session("None")
    st.button(key = "next1",label= "next", on_click=main)

    components.html ("""<script>
                const bt = window.parent.document.querySelectorAll('.stButton > Button');
                 
                for (var i = 0; i < bt.length; i++) {
                bt[i].click(); // Click each button
                bt[i].style.display = "none";
                }
                console.log("done");
                </script>""")

# lock = threading.Lock()
# label_container = {"label":None}
result_queue = queue.Queue()


def callback(frame):
    global result_queue
    img = frame.to_ndarray(format="bgr24")
    img, res = detect(img=img)

    print(res)
    if res and float(res.split()[1]) > 0.7:
    # #     # set the value of pred[1] to some variable on the main thread
        result_queue.put(res)
        
    return av.VideoFrame.from_ndarray(img, format="bgr24")

def webcam():
    
    col1, col2 = st.columns(2)
    st.header("Object detection webcam")
    with col1:
        webcam_ = webrtc_streamer(
            key="object-detection",
            mode=WebRtcMode.SENDRECV,

            video_frame_callback=callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
            )
        
        flag = False
        while webcam_.state.playing:
            try:
                pred = result_queue.get_nowait()
                def res_():
                    st.image(caption="throw here", image="https://img.kingfisherdirect.co.uk/media/catalog/product/L/E/LEALIENBUDDY_3_spacebuddy-alien-recycling-bin-84-litre.jpg?width=600&height=600&store=kingfisherdirect&image-type=image")
                    st.write("Object Detected:", pred)
                    time.sleep(4)
                    reset_user_session("qr")
                    st.button(key = "next0",label= "next", on_click=main)
                    components.html ("""<script>
                    const bt = window.parent.document.querySelectorAll('.stButton > Button');
                        
                    for (var i = 0; i < bt.length; i++) {
                    bt[i].click(); // Click each button
                    bt[i].style.display = "none";
                    }
                    console.log("done");
                    </script>""")
                with col2:
                    res_()
            except queue.Empty:
                pass
            # Process the detected object here in the main thread
        

    with col2:
        st.write("🌍") 

        
# binscreen()
# qrscreen()
# webcam()

def main():
    
    if "_session" not in st.session_state or st.session_state["_session"] == "None":
        st.session_state["_session"] = "None"
        with st.spinner('Please wait...'):
            webcam()
    elif  st.session_state["_session"] == "qr":
        with st.spinner('Please wait...'):
            qrscreen()
    elif  st.session_state["_session"] == "bins":
        with st.spinner('Please wait...'):
            binscreen()

# reset_user_session("qr")

main()