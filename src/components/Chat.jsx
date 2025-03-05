import { useState, useEffect, useRef } from "react";
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import axios from "axios";
import submitArrow from "../assets/submit_arrow.svg";
import fullLogo from "../assets/pillar_logo_full.svg";
import blackLogo from "../assets/pillar_icon_black.svg";


export const Chat = () => {
    const { chatId } = useParams();
    const key = `chat-${chatId}`;

    const [msgs, setMsgs] = useState(() => {
        const savedMsgs = window.sessionStorage.getItem(`${key}`);
        return savedMsgs ? JSON.parse(savedMsgs) : [];
    });
    const msgVal = useRef();

    useEffect(() => {
        const savedMsgs = sessionStorage.getItem(`${key}`);

        setMsgs(savedMsgs ? JSON.parse(savedMsgs) : []);
    }, [chatId]);

    useEffect(() => {
        window.sessionStorage.setItem(`${key}`, JSON.stringify(msgs));
    }, [msgs, chatId])

    const getResp = (e) => {
        e.preventDefault();

        const currMsg = msgVal.current.value;

        e.target.querySelector("input").value = "";

        // create deep copy
        let newMsgs = [...msgs, { "usr": currMsg }];

        setMsgs(newMsgs);

        // get response from API server
        axios.post("/api/get-resp", { prompt: msgVal })
            .then((resp) => {
                console.log(resp.data)
                // deep copy of resp msg list
                // add new data to list
                newMsgs = [...newMsgs, { "res": resp.data }];

                // update state with new msgs
                setMsgs(newMsgs);
            })
            .catch((err) => console.error(`Error in getResp: ${err}`));
    };

    function ResponseMessage({ msg, idx, timeout = 1000 }) {
        const [finishedMsg, setFinishedMsg] = useState(() => {
            const savedState = sessionStorage.getItem(`${key}_${idx}`);
            console.log(`${key}_${idx} -> ${savedState}`)
            return savedState ? JSON.parse(savedState) : false;
        });
        const [contents, setContents] = useState(() => {
            return finishedMsg ? msg.res : "";
        });
        let i = 0;

        if (contents === "" && !finishedMsg) {
            const interval = setInterval(() => {
                if (i < msg.res.length) {
                    i++;
                    setContents(msg.res.slice(0, i));
                } else {
                    clearInterval(interval);
                    sessionStorage.setItem(`${key}_${idx}`, JSON.stringify(true));
                    setFinishedMsg(true);
                }
            }, timeout);
        }

        return (
            <>
                <div
                    className="resp-profile profile"
                >
                    <img key={i} src={blackLogo} alt="" />
                </div>
                <div
                    className="resp-msg msg"
                >
                    <ReactMarkdown components={{ p: "span" }}>
                        {contents}
                    </ReactMarkdown>
                    {!finishedMsg &&
                        <svg
                            viewBox="8 0 8 16"
                            xmlns="http://www.w3.org/2000/svg"
                            className="cursor"
                        >
                            <rect x="10" y="2" width="6" height="14" fill="#ffffff83" />
                        </svg>
                    }
                </div>
            </>
        )
    }

    function UserMessage({ msg }) {
        return (
            <>
                <div
                    className="user-profile profile"
                >
                </div>
                <div
                    className="user-msg msg"
                >
                    {msg.usr}
                </div>
            </>
        )
    }

    return (
        <div className="container">
            <div className="background">
                {msgs.length < 1 ? <img src={fullLogo} alt="" /> : <></>}
            </div>
            <div className="message-list">
                {msgs.map((msg, i) => {
                    if (msg !== undefined) {
                        return (
                            Object.keys(msg).includes("usr") ? <UserMessage msg={msg} key={i} /> : <ResponseMessage msg={msg} idx={i} timeout={50} key={i} />
                        )
                    }
                })}
            </div>

            <form className="chat-bar" onSubmit={(e) => {
                getResp(e);
            }}>
                <input
                    type="text"
                    placeholder="Message Pillar"
                    ref={msgVal}
                />
                <button
                    type="button"
                >
                    <img src={submitArrow} alt="" />
                </button>
            </form>
        </div>
    );
}



