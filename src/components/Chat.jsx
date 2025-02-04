import { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vs } from "react-syntax-highlighter/dist/esm/styles/prism";
import submitArrow from "../assets/submit_arrow.svg";
import fullLogo from "../assets/pillar_logo_full.svg";
import blackLogo from "../assets/pillar_icon_black.svg";

export const Chat = () => {
  const { chatId } = useParams();
  const key = `chat-${chatId}`;

  const [userMsgs, setUserMsgs] = useState(() => {
    const savedUserMsgs = window.sessionStorage.getItem(`${key}-user`);
    return savedUserMsgs ? JSON.parse(savedUserMsgs) : [];
  });
  const [respMsgs, setRespMsgs] = useState(() => {
    const savedRespMsgs = window.sessionStorage.getItem(`${key}-resp`);
    return savedRespMsgs ? JSON.parse(savedRespMsgs) : [];
  });

  const [combinedMsgs, setCombinedMsgs] = useState([]);
  const [msgVal, setMsgVal] = useState("");

  useEffect(() => {
    const savedUserMsgs = sessionStorage.getItem(`${key}-user`);
    const savedRespMsgs = sessionStorage.getItem(`${key}-resp`);

    setUserMsgs(savedUserMsgs ? JSON.parse(savedUserMsgs) : []);
    setRespMsgs(savedRespMsgs ? JSON.parse(savedRespMsgs) : []);
  }, [chatId]);  

  useEffect(() => dispMsgs(), [userMsgs, respMsgs]);

  useEffect(() => {
    window.sessionStorage.setItem(`${key}-user`, JSON.stringify(userMsgs));
    window.sessionStorage.setItem(`${key}-resp`, JSON.stringify(respMsgs));
  }, [userMsgs, respMsgs, chatId])

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
      .catch((err) => console.error(`Error in getResp: ${err}`)
);
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
                  className={`${i % 2 === 0 ? "user-profile" : "resp-profile"
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
