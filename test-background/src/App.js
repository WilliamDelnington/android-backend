import logo from './logo.svg';
import './App.css';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Signup from './Auth/Signup';
import Login from './Auth/Login';
import Main from './Main/Main';
import Video from './Media/Video';
import Article from './Media/Article';
import ForgotPassword from './Auth/ForgotPassword';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/video/:videoId" element={<Video />} />
        <Route path="/article/:articleId" element={<Article />} />
        <Route path="/signup" element={<Signup />}/>
        <Route path="/login" element={<Login />} />
        <Route path="/forgotPassword" element={<ForgotPassword />}/>
      </Routes>
    </Router>
  );
}

export default App;
// <div className="App">
    //   <header className="App-header">
    //     <img src={logo} className="App-logo" alt="logo" />
    //     <p>
    //       Edit <code>src/App.js</code> and save to reload.
    //     </p>
    //     <a
    //       className="App-link"
    //       href="https://reactjs.org"
    //       target="_blank"
    //       rel="noopener noreferrer"
    //     >
    //       Learn React
    //     </a>
    //   </header>
    // </div>