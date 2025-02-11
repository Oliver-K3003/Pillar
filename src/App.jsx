// style sheet imports
import "./App.css";
// general imports
import { useState } from "react";
import { Sidebar, Menu, MenuItem, SubMenu } from "react-pro-sidebar";
import { BrowserRouter as Router, Routes, Route, Link, useParams } from "react-router-dom";
import { Chat } from './components/Chat.jsx';
// asset imports
import newChat from './assets/chat-add-icon.svg'
import fullLogo from "./assets/pillar_logo_full.svg";

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
    const [chatIds, setChatIds] = useState([0]);

    const createNewChat = () => {
        const currId = chatIds[chatIds.length - 1];
        setChatIds([...chatIds, currId + 1]);
    }

    return (
        <Router>
            <div className="container">
      <GithubLogin/>
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
                        <Menu title="Pillar">
                            <SubMenu label="Chats">
                                {chatIds.map((id) =>
                                    <MenuItem key={id} id={id}>
                                        <Link className="chat-link" to={`/chat/${id}`}>Chat {id + 1}</Link>
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
