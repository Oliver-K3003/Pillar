import React from "react";
import { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import axios from "axios";
import submitArrow from "../assets/submit_arrow.svg";
import fullLogo from "../assets/pillar_logo_full.svg";
import blackLogo from "../assets/pillar_icon_black.svg";

function ResponseMessage({ msg, timeout = 1000 }) {
    const [contents, setContents] = useState(msg.isNew ? "" : msg.response);
    const [finishedMsg, setFinishedMsg] = useState(!msg.isNew);
    let i = 0;

    if (contents === "" && !finishedMsg) {
        const interval = setInterval(() => {
            if (i < msg.response.length) {
                i++;
                setContents(msg.response.slice(0, i));
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
                {msg.prompt}
            </div>
        </>
    )
}

export const Chat = () => {
    const { chatId } = useParams();
    const [msgs, setMsgs] = useState([])
    const [msgVal, setMsgVal] = useState("");

    useEffect(() => {
        setMsgs([]);
        axios.get(`/api/conversation/messages/get`, { params: { conversation_id: chatId } })
            .then((response) => {
                setMsgs(response.data.messages || []);
            })
            .catch((err) => console.error(`Error fetching messages: ${err}`));
    }, [chatId]);


    const handleInput = (e) => {
        setMsgVal(e.target.value);
    };

    const getResp = (e) => {
        e.preventDefault();

        e.target.querySelector("input").value = "";

        // create deep copy
        let newMsgs = [...msgs, { prompt: msgVal }];

        setMsgs(newMsgs);
        // get response from API server
        axios.post(`/api/get-resp`, { prompt: msgVal, chatId: chatId })
            .then((resp) => {
                // deep copy of resp msg list
                // add new data to list
                newMsgs = [...newMsgs, { response: resp.data, isNew: true }];

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
                            <React.Fragment key={i}>
                                {msg.prompt && <UserMessage msg={msg} key={`${i}-user`} />}
                                {msg.response && <ResponseMessage msg={msg} timeout={1} key={`${i}-response`} />}
                            </React.Fragment>
                        );
                    } else {
                        return null;
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