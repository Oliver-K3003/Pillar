import { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import axios from "axios";
import submitArrow from "../assets/submit_arrow.svg";
import fullLogo from "../assets/pillar_logo_full.svg";
import blackLogo from "../assets/pillar_icon_black.svg";

function ResponseMessage({ msg, timeout = 1000 }) {
    const [contents, setContents] = useState("");
    const [finishedMsg, setFinishedMsg] = useState(false);
    let i = 0;

    if (contents === "" && !finishedMsg) {
        const interval = setInterval(() => {
            if (i < msg.res.length) {
                i++;
                setContents(msg.res.slice(0, i));
            } else {
                clearInterval(interval);
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
                {contents}
                {!finishedMsg &&
                    <svg
                        viewBox="8 0 8 16"
                        xmlns="http://www.w3.org/2000/svg"
                        className="cursor"
                    >
                        <rect x="10" y="2" width="6" height="14" fill="#2c2b2b" />
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

export const Chat = () => {
    const { chatId } = useParams();
    const key = `chat-${chatId}`;

    const [msgs, setMsgs] = useState(() => {
        const savedMsgs = window.sessionStorage.getItem(`${key}`);
        return savedMsgs ? JSON.parse(savedMsgs) : [];
    });
    const [msgVal, setMsgVal] = useState("");

    useEffect(() => {
        const savedMsgs = sessionStorage.getItem(`${key}`);

        setMsgs(savedMsgs ? JSON.parse(savedMsgs) : []);
    }, [chatId]);

    useEffect(() => {
        window.sessionStorage.setItem(`${key}`, JSON.stringify(msgs));
    }, [msgs, chatId])

    const handleInput = (e) => {
        setMsgVal(e.target.value);
    };

    const getResp = (e) => {
        e.preventDefault();

        e.target.querySelector("input").value = "";

        // create deep copy
        let newMsgs = [...msgs, { "usr": msgVal }];

        setMsgs(newMsgs);
        // get response from API server
        axios
            .post("http://localhost:5000/get-resp", { prompt: msgVal })
            .then((resp) => {
                // deep copy of resp msg list
                // add new data to list
                newMsgs = [...newMsgs, { "res": resp.data }];

                // update state with new msgs
                setMsgs(newMsgs);
            })
            .catch((err) => console.error(`Error in getResp: ${err}`));
    };

    return (
        <div className="container">
            <div className="background">
                {msgs.length < 1 ? <img src={fullLogo} alt="" /> : <></>}
            </div>
            <div className="message-list">
                {msgs.map((msg, i) => {
                    if (msg !== undefined) {
                        return (
                            Object.keys(msg).includes("usr") ? <UserMessage msg={msg} key={i} /> : <ResponseMessage msg={msg} timeout={50} key={i} />
                        )
                    }
                })}
            </div>

            <form className="chat-bar" onSubmit={(e) => getResp(e)}>
                <input
                    type="text"
                    placeholder="Message Pillar"
                    onChange={handleInput}
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



