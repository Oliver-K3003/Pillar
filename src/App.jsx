import "./App.css";
import { useState, useEffect } from "react";
import axios from "axios";
// asset imports
import submitArrow from "./assets/submit_arrow.svg";
import fullLogo from "./assets/pillar_logo_full.svg";
import blackLogo from "./assets/pillar_icon_black.svg";

/* 
TODO
  [ ] fix outline when char bar is focused
  [ ] iron out profile pictures (not sure if we want user to have one)
  [ ] clean up colour scheme
  [ ] remove logo on first prompt
  [ ] optimize for extension format
  [ ] improve function of given text input to react more similarly to competitor models
  [ ] decide layout of prompts and answers (options currently exist -> see comments in App.css 
    under user-profile, resp-profile, & resp-msg)
*/

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

    newUserMsgs.push(msgVal);

    setUserMsgs(newUserMsgs);

    // sessionStorage.setItem("user-msgs", JSON.stringify(newUserMsgs));
    // get response from API server
    axios
      .get("http://localhost:5000/get-resp")
      .then((resp) => {
        // deep copy of resp msg list
        let newRespMsgs = JSON.parse(JSON.stringify(respMsgs));

        // add new data to list
        newRespMsgs.push(resp.data);

        // update state with new msgs
        setRespMsgs(newRespMsgs);
        // update session storage with new msgs
        // sessionStorage.setItem("resp-msgs", JSON.stringify(newRespMsgs));
      })
      .catch((err) => console.error(`Error in getResp: ${err}`));
  };

  const dispMsgs = () => {
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
              <>
                <div
                  // replace user-profile with common 'hidden' class if we decide to go forth with that display method
                  className={`${
                    i % 2 === 0 ? "user-profile" : "resp-profile"
                  } profile`}
                >
                  <img src={blackLogo} alt="" />
                </div>
                <div
                  key={i}
                  className={`${i % 2 === 0 ? "user-msg" : "resp-msg"} msg`}
                >
                  {msg}
                </div>
              </>
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
