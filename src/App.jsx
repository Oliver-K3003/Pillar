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
  const [isSideNavCollapsed, setSideNavCollapsed] = useState(false);
  const [chatIds, setChatIds] = useState([0]);

  const createNewChat = () => {
    const currId = chatIds[chatIds.length - 1];
    setChatIds([...chatIds, currId + 1]);
  }

  return (
    <Router>
      <div className="sideNav">
        <Sidebar collapsed={isSideNavCollapsed}>
          <div className="sideNavHeader">
            <button className="headerButton" type="button" onClick={() => setSideNavCollapsed(!isSideNavCollapsed)}>
              {!isSideNavCollapsed ? <img src={collapseIcon} alt="" /> : <img src={expandIcon} alt="" />}
            </button>
            {!isSideNavCollapsed ? <button className="headerButton" type="button" onClick={createNewChat}>
              <img src={newChat} alt=""/>
            </button> : null}
          </div>
          <Menu title="Pillar">
            <SubMenu label="Chats">
              {chatIds.map((id) => 
                <MenuItem key={id} id={id}>
                  <Link to={`/chat/${id}`}>Chat {id + 1}</Link>
                </MenuItem>
              )}
            </SubMenu>
          </Menu>
        </Sidebar>
      </div>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/chat/:chatId" element={<Chat />} />
      </Routes>
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
