import "./App.css";
import { useState, useEffect } from "react";
import axios from "axios";
// asset imports
import submitArrow from "./assets/submit_arrow.svg";
import fullLogo from "./assets/pillar_logo_full.svg";

function App() {
  const [userMsgs, setUserMsgs] = useState([]);
  const [respMsgs, setRespMsgs] = useState([]);
  const [combinedMsgs, setCombinedMsgs] = useState([]);
  const [msgVal, setMsgVal] = useState("");

  useEffect(() => dispMsgs(), [userMsgs]);

  useEffect(() => dispMsgs(), [respMsgs]);

  const handleInput = (e) => {
    setMsgVal(e.target.value);
  };

  const getResp = () => {
    // create deep copy
    let newUserMsgs = JSON.parse(JSON.stringify(userMsgs));

    console.log(newUserMsgs);

    newUserMsgs.push(msgVal);

    console.log(`setting usermsgs: ${newUserMsgs}`);
    setUserMsgs(newUserMsgs);

    // sessionStorage.setItem("user-msgs", JSON.stringify(newUserMsgs));
    // get response from API server
    axios
      .get("http://localhost:5000/get-resp")
      .then((resp) => {
        // deep copy of resp msg list
        let newRespMsgs = JSON.parse(JSON.stringify(respMsgs));

        console.log(newRespMsgs);
        // add new data to list
        newRespMsgs.push(resp.data);

        console.log(`setting respmsgs: ${newRespMsgs}`);
        // update state with new msgs
        setRespMsgs(newRespMsgs);
        console.log("testresp" + respMsgs);
        // update session storage with new msgs
        // sessionStorage.setItem("resp-msgs", JSON.stringify(newRespMsgs));
      })
      .catch((err) => console.error(`Error in getResp: ${err}`));
  };

  const dispMsgs = () => {
    console.log(`usermgs: ${userMsgs}`);
    console.log(`respmsgs: ${respMsgs}`);
    // ensure msgs exist
    if (userMsgs !== null) {
      if (respMsgs !== null) {
        // if user and resp msgs exist alternate them
        let msgChain = [];
        let l = Math.min(userMsgs.length, respMsgs.length);

        for (let i = 0; i < l; i++) {
          msgChain.push(userMsgs[i], respMsgs[i]);
        }
        msgChain.push(...userMsgs.slice(l), ...respMsgs.slice(l));

        setCombinedMsgs(msgChain);
      } else {
        setCombinedMsgs(userMsgs);
      }
    } else {
      return <></>;
    }
  };

  return (
    <div className="container">
      <div className="background">
        <img src={fullLogo} alt="" />
      </div>
      <div className="message-list">
        {
          <>
            {combinedMsgs.map((msg, i) => (
              <div
                key={i}
                className={`${i % 2 === 0 ? "resp-msg" : "user-msg"} msg`}
              >
                {msg}
              </div>
            ))}
          </>
        }
      </div>
      <div className="chat-bar">
        <input
          type="text"
          placeholder="Message Pillar"
          onChange={handleInput}
        />
        <button
          type="button"
          onClick={() => {
            getResp();
          }}
        >
          <img src={submitArrow} alt="" />
        </button>
      </div>
    </div>
  );
}

export default App;
