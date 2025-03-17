// style sheet imports
import "./App.css";
// general imports
import { useState, useEffect } from "react";
import { Sidebar, Menu, MenuItem, SubMenu } from "react-pro-sidebar";
import { BrowserRouter as Router, Routes, Route, Link, useParams } from "react-router-dom";
import { Chat } from './components/Chat.jsx';
import axios from "axios";
// asset imports
import newChat from './assets/chat-add-icon.svg'
import fullLogo from "./assets/pillar_logo_full.svg";
import deleteIcon from './assets/delete-button.svg';
import collapseIcon from "./assets/collapse-icon.svg";
import expandIcon from "./assets/expand-icon.svg";
import GithubLogin from "./components/GithubLogin";

/* 
TODO
  [ ] iron out profile pictures (not sure if we want user to have one)
  [ ] clean up color scheme
  [ ] optimize for extension format
  [ ] fix retyping on reload/change chat
*/

function App() {
    const [isSideNavCollapsed, setSideNavCollapsed] = useState(false);
    const [chatIds, setChatIds] = useState([]);
    const [user, setUser] = useState("");

    // Trigger the API call for Github User Info.
    useEffect(() => {
        axios.get(`/api/github/user-info`)
            .then((response) => {
                console.log(response.data.login);
                setUser(response.data.login);
            })
            .catch((error) => {
                console.log("Error getting user info.");
            });
    }, []);

    // Use effect to send user to DB *after* state is updated
    useEffect(() => {
        if (user) { // Only run when user is set
            console.log("Sending username to DB:", user);
            axios.post(`/api/db/user/add-or-update`, { username: user })
                .catch((error) => console.error("Error updating user in DB:", error));
        }
    }, [user]);

    // Check for the user state AFTER update and get existing conversation IDs.
    useEffect(() => {
        if (user) {
            console.log("User state updated to:", user);
            axios.get(`/api/db/conversation/getChatIds`, { params: { user } })
                .then((response) => {
                    setChatIds(response.data.ids)
                })
        }
    }, [user]);

    // Show obtained chatIDs after obtained.
    useEffect(() => {
        if (chatIds) {
            console.log("Got chatIDs: " + chatIds);
        }
    })

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
        <Router>
            <div className="container">
                <GithubLogin setUser={setUser}/>
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
                </div>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/chat/:chatId" element={user ? <Chat /> : <Home />} />
                </Routes></div>
        </Router>
    );
}

const Home = () => (
    <div className="container">
        <div className="background">
            <img src={fullLogo} alt="" />
        </div>
    </div>
);



export default App;
