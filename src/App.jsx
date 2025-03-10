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
import GithubUser from "./components/GithubUser.jsx";
import GithubButton from "./components/GithubButton.jsx";
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

    useEffect(() => {
        axios.get(`/api/github/user-info`)
            .then((response) => {
             setUser(response.data.login);
             console.log(user);
      })
    }, [])

    useEffect(() => {
        axios.get(`api/conversation/get`, {params: {user}})
            .then((response) => {
                setChatIds(response.data.ids)
                console.log(chatIds)
            })
    }, [user])

    const createNewChat = () => {
        axios.post(`/api/conversation/create`, {username: user})
            .then((response) => {
                setChatIds([...chatIds, response.data.id])
            })
    }

    return (
        <Router>
            <div className="container">
                <GithubLogin />
                <GithubUser />
                <GithubButton/>
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
                                            <button className="headerButton"><img className="headerButtonIcon" src={deleteIcon} /></button>
                                        </div>
                                    </MenuItem>
                                )}
                            </SubMenu>
                        </Menu>
                    </Sidebar>
                </div>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/chat/:chatId" element={<Chat />} />
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
