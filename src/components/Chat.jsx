import React from "react";
import ReactMarkdown from 'react-markdown'
import { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import axios from "axios";
import submitArrow from "../assets/submit_arrow.svg";
import fullLogo from "../assets/pillar_logo_full.svg";
import blackLogo from "../assets/pillar_icon_black.svg";
import { Oval } from 'react-loader-spinner';

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
                {msg.prompt}
            </div>
        </>
    )
}

export const Chat = () => {
    const { chatId } = useParams();
    const [msgs, setMsgs] = useState([])
    const [msgVal, setMsgVal] = useState("");
    const [loading, setLoading] = useState(false);
    const [isSideNavCollapsed, setSideNavCollapsed] = useState(false);

    useEffect(() => {
        setLoading(true);
        setMsgs([]);
        axios.get(`/api/conversation/messages/get`, { params: { conversation_id: chatId } })
            .then((response) => {
                setMsgs(response.data.messages || []);
            })
            .catch((err) => console.error(`Error fetching messages: ${err}`))
            .finally(() => setLoading(false));
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

    // Function to create new chat.
    const createNewChat = () => {
        axios.post(`/api/db/conversation/create`, { username: user })
            .then((response) => {
                setChatIds([...chatIds, response.data.id])
            })
    }

    // Function to delete chat.
    const deleteChat = (id) => {
        axios.post(`/api/db/conversation/delete`, { conversation_id: id })
            .then((response) => {
                if (response.status === 200) {
                    setChatIds(chatIds.filter(chatId => chatId !== id))
                }
            })
            .catch((error) => {
                console.error(`Error deleting conversation with id ${id}:`, error);
            });
    }

    return (
        <div className="container">
            <div className="sideNav">
                <Sidebar collapsed={isSideNavCollapsed}>
                    <div className="sideNavHeader">
                        <button className="headerButton" type="button" onClick={() => setSideNavCollapsed(!isSideNavCollapsed)}>
                            {!isSideNavCollapsed ? <img className="headerButtonIcon" src={collapseIcon} alt="" /> : <img className="headerButtonIcon" src={expandIcon} alt="" />}
                        </button>
                        {!isSideNavCollapsed ? <button className="headerButton" type="button" onClick={createNewChat}>
                            <img className="headerButtonIcon" src={newChat} alt="" />
                        </button> : null}
                    </div>
                    <Menu className="chat-container" title="Pillar" menuItemStyles={{
                        button: ({ level, active, disabled }) => {
                            if (level === 0 || level === 1) {
                                return {
                                    transition: "backgroundColor 200ms ease-in-out",
                                    zIndex: "100",
                                    "&:hover": {
                                        backgroundColor: "#403f3f !important",
                                        zIndex: "100"
                                    }
                                }
                            }
                        },
                    }
                    }>
                        <SubMenu label="Chats">
                            {chatIds.map((id) =>
                                <MenuItem key={id} id={id}>
                                    <div className="menuItemContainer">
                                        <Link className="chat-link" to={`/chat/${id}`}>Chat {id}</Link>
                                        <button className="headerButton" onClick={() => deleteChat(id)}><img className="headerButtonIcon" src={deleteIcon} /></button>
                                    </div>
                                </MenuItem>
                            )}
                        </SubMenu>
                    </Menu>
                </Sidebar>
                {loading ? (
                    <Oval
                        height={250}
                        width={250}
                    />
                ) : (
                    <>
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
                    </>
                )}
            </div>
        </div>
            );
}
