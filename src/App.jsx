// style sheet imports
import "./App.css";
// general imports
import { useState, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
// plugin imports
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vs } from "react-syntax-highlighter/dist/esm/styles/prism";
// asset imports
import submitArrow from "./assets/submit_arrow.svg";
import fullLogo from "./assets/pillar_logo_full.svg";
import blackLogo from "./assets/pillar_icon_black.svg";
import GithubLogin from "./components/GithubLogin";

/* 
TODO
  [x] add basic model support
  [ ] decide on code display format options here(https://github.com/react-syntax-highlighter/react-syntax-highlighter/blob/master/AVAILABLE_STYLES_PRISM.MD)
  [ ] fix outline when char bar is focused
  [ ] iron out profile pictures (not sure if we want user to have one)
  [ ] clean up colour scheme
  [x] remove logo on first prompt
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
    console.log(msgVal);
    // sessionStorage.setItem("user-msgs", JSON.stringify(newUserMsgs));
    // get response from API server
    axios
      .post("http://localhost:5000/get-resp", { prompt: msgVal })
      .then((resp) => {
        console.log(resp.data);
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
      <GithubLogin/>
      <div className="background">
        {userMsgs.length < 1 ? <img src={fullLogo} alt="" /> : <></>}
      </div>
      <div className="message-list">
        {
          <>
            {combinedMsgs.map((msg, i) => (
              <>
                <div
                  key={i}
                  // replace user-profile with common 'hidden' class if we decide to go forth with that display method
                  className={`${
                    i % 2 === 0 ? "user-profile" : "resp-profile"
                  } profile`}
                >
                  <img key={i} src={blackLogo} alt="" />
                </div>
                <div
                  key={i}
                  className={`${i % 2 === 0 ? "user-msg" : "resp-msg"} msg`}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline && match ? (
                          <SyntaxHighlighter
                            children={String(children).replace(/\n$/, "")}
                            style={vs}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          />
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {msg}
                  </ReactMarkdown>
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
