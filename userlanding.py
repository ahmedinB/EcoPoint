import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from collections import defaultdict

def getconn():
    # mysql.connect("mysql://root:root@localhost:3307/mydb")
    return st.connection(
        "local_db",
        type="sql",
        url="mysql://root:root@localhost:3307/mydb"
    )



#  user - ID username password email score 
# transactionn - ID username type/score binID DateTime
# Bin - binID isFull location
# Rewards - ID name provider 

def login(collectPt = False):
    # Set the title and a brief description of the app
    st.title("EcoPoint")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # auth

    def action_call_login():
        if not firebase_admin._apps:
            cred = credentials.Certificate("smartbin-c09bd-firebase-adminsdk-9k368-b97ae8a87a.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL':"https://smartbin-c09bd-default-rtdb.europe-west1.firebasedatabase.app/"
                })
        ref = db.reference()
        try:
            # Query to retrieve data where username equals the specified value
            uref =  ref.child("users").order_by_child("username").equal_to(username).get()
            
            k, userdata = None, None
            for k, userdata in uref.items():
                k, userdata = k, userdata
            
            if username == "admin" and password == "admin":
                st.session_state["user_session"] = "admin"

            elif userdata["password"]!=password or userdata is None:
                st.warning("Incorrect username or password!")
                return
            else:
                # collect point from the flag
                if collectPt:
                    newtransaction =  ref.child("transactions").child(key).get()
                    
                    if newtransaction["username"] == "default_value":
                        try:
                            # st.progress("Please wait...")
                            score = int(newtransaction["score"]) + int(userdata["score"])
                            
                            ref.child("users").child(k).update({"score":score})
                            ref.child("transactions").child(key).update({"username":username})    
                            st.success("Successfuly collected points!")
                        except Exception as inst:
                            st.warning("Error with db.") 
                            st.warning(inst)   
                    else:
                        st.experimental_set_query_params()
                        st.warning("There point keys are invalid!")

                    
                # login
                st.session_state["user_session"] = username

        except Exception as e:
            st.warning("User not found! Please register...")
            st.warning(e)
    def action_call_register():
        st.experimental_set_query_params()
        st.session_state["user_session"] = "register"
    
    
    login = st.button("Login", type="primary", on_click=action_call_login, use_container_width=True) 
    register = st.button("Register", on_click=action_call_register) 
    
        

    # Add a footer to the page
    st.sidebar.write("© 2023 EcoPoint Inc.")

def register():
    # Set the title and a brief description of the app
    st.title("EcoPoint")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    


    def action_register():
        # validate inputs  * username has to be unique

        # insert inputs into database
        try:
            def is_username_unique(username):
                snapshot = ref.order_by_child("username").equal_to(username).get()

                return not snapshot 
            # st.session_state["user_session"] = username
            if not firebase_admin._apps:
                cred = credentials.Certificate("smartbin-c09bd-firebase-adminsdk-9k368-b97ae8a87a.json")
                firebase_admin.initialize_app(cred, {
                    'databaseURL':"https://smartbin-c09bd-default-rtdb.europe-west1.firebasedatabase.app/"
                    })
            ref = db.reference("/users")
            data = {
                "username": username,
                "email": email,
                "password": password,
                "score": 50
            }
            
            flag = is_username_unique(username)
            if flag:
                ref.push(data)
                st.session_state["user_session"] = username
            else:
                st.warning("This username is already taken.")
        except Exception as e:
            st.warning(e)

    st.button("Register", type="primary", on_click=action_register, use_container_width=True)
    st.button("Go Back", on_click=reset_user_session,)

    
    # Add a footer to the page
    st.sidebar.write("© 2023 EcoPoint Inc.")

def adminprofile():
    # Set the title and a brief description of the app
    st.title("Admin Dashboard")

    # Add admin profile on the side bar
    st.sidebar.write("# EcoPoint")
    st.sidebar.header("Hello Admin,")
    # st.sidebar.markdown("<p>"+ user_.get("email")[0] +"</p>", unsafe_allow_html=True)
    # st.sidebar.write("#", user_.get("score")[0])

    # number of users / transations and bins
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("users", 22, 3)
    with col2:
        st.metric("transactions", "3000", 495)
    with col3:
        st.metric("bins", "12")

    # transaction in a week /delta?
    # bins map 
    # Create a sample DataFrame with latitude, longitude, and bin fullness
    data = {
        'LATITUDE': np.random.uniform(24.485187, 24.489028, 10),  # Random latitude values
        'LONGITUDE': np.random.uniform(54.351187, 54.353803, 10),  # Random longitude values
        'IsFull': np.random.choice(['#748729', '#ab400c', '#ffd731'], size=10)  # Random fullness status
    }
    # 24.485187, 54.351187 24.489028, 54.353803
    df = pd.DataFrame(data)

    # Generate random x and y data
    x = [_ for _ in range(10)]  # 10 random x values between 0 and 100
    y = [np.random.randint(0, 100) for _ in range(10)]  # 10 random y values between 0 and 100

    fig, ax = plt.subplots()
    # Create a line graph
    ax.plot(x, y, marker='o', linestyle='-')

    # Remove the axis numbers (ticks) from both x and y axes
    # ax.set_xticks([])
    # ax.set_yticks([])

    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Line Graph')

    col1, col2 = st.columns(2)
    # Display the plot using st.pyplot()
    with col2:
        st.pyplot(fig)
    # Create a map using st.map
    with col1:
        st.map(df, color= "IsFull", size=10, zoom=16)

    # show top weekly reward receivers 
    
    st.sidebar.button("logout", on_click=reset_user_session)

    # Add a footer to the page
    st.sidebar.write("© 2023 EcoPoint Inc.")

def userprofile():
    if not firebase_admin._apps:
        cred = credentials.Certificate("smartbin-c09bd-firebase-adminsdk-9k368-b97ae8a87a.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL':"https://smartbin-c09bd-default-rtdb.europe-west1.firebasedatabase.app/"
            })
    ref = db.reference()
    # Query to retrieve data where username equals the specified value
    uref =  ref.child("users").order_by_child("username").equal_to(st.session_state["user_session"]).get()
    k, userdata = None, None
    for k, userdata in uref.items():
        k, userdata = k, userdata
    userkey = k
    # Set the title and a brief description of the app
    st.sidebar.write("# EcoPoint")

    # show statistics and set of rewards to incentivise 

    st.subheader("Top rewards this week")
    rewardref = ref.child("rewards").get()
        # Transpose the result
    d_ = defaultdict(list)
    for k, data in rewardref.items():
        d_["provider"].append(data["provider"])
        d_["description"].append(data["description"])
        d_["escore"].append(data["escore"])
        # d_["description"].append(data["description"])
        # d_["description"].append(data["description"])
    
    st.dataframe(d_)
    
    def redeem():
        # Get the selected reward information
        rewardref0 = ref.child("rewards").order_by_child("description").equal_to(selected_reward).get()
        _, reward_ = None, None
        for _,reward_ in rewardref0.items():
            _,reward_ = _,reward_
        rewardref0 = reward_ 

        if userdata["score"] >= rewardref0["escore"]: 
            # substract form total point here
            score = userdata["score"] - rewardref0["escore"]
            print(score)
            ref.child("users").child(userkey).update({"score":score})
            st.success(f"Redeemed '{selected_reward}'!")
            voucher = rewardref0["voucher"]
            st.success(f"Voucher or Coupon: {voucher}")
            
        else:
            st.warning(f"Reward minimum score is not reached!")

    selected_reward = st.selectbox("Select a reward to redeem:", d_["description"])
    

    st.button(label = "Redeem",type="primary",use_container_width=True, on_click= redeem)
    # Add a button to redeem




    # show top weekly reward receivers # needs reward draw database

    # Transaction History
    st.subheader("Recent Transcations")
    transactionData = ref.child("transactions").order_by_child("username").equal_to(userdata["username"]).get()

    df_ = defaultdict(list)

    for k, data in transactionData.items():
        df_["binID"].append(data["binID"])
        df_["datetime"].append(datetime.fromtimestamp(data["datetime"]).date())
        df_["score"].append(data["score"])

    st.dataframe(df_)
        

    # Add user profile on the side bar

    title = "Hello " + userdata["username"].capitalize() + ","
    st.sidebar.header(title)
    st.sidebar.markdown("<p>"+ userdata["email"] +"</p>", unsafe_allow_html=True)
    st.sidebar.metric("Earned points", userdata["score"])
    
    st.sidebar.button("logout", on_click=reset_user_session)
    
    # Add a footer to the page
    st.sidebar.write("© 2023 EcoPoint Inc.")

def reset_user_session():
    st.session_state["user_session"] = "None"

# Parse the URL to get query parameters
query_params = st.experimental_get_query_params()
if len(query_params)>0:
    if "key" in query_params:
        key =  query_params["key"][0]
        username = ""
        if "user_session" in st.session_state and (st.session_state["user_session"] != "None" or st.session_state["user_session"] != "register" or st.session_state["user_session"] != "admin"):
            username = st.session_state["user_session"]
            # then add the user name if the key is in db   
            
        else:
            # go to the form and take username
            st.session_state["collectPt"] = key
            login(collectPt = True)
                
    else:
        st.warning("404")

elif "user_session" not in st.session_state:
    st.session_state["user_session"] = "None"
    login()
    

elif st.session_state["user_session"] == "None":
    login()

elif st.session_state["user_session"] == "register":
    register()

elif st.session_state["user_session"] == "admin":
    adminprofile()

else:
    userprofile()


