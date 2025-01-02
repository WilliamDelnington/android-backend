import React, {useEffect, useState} from 'react'
import { useNavigate } from 'react-router-dom'
import Video from './Media/Video'

export default function Main() {
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [username, setUsername] = useState("")

    useEffect(() => {
        setIsAuthenticated(localStorage.getItem("is_authenticated") === "true")
        setUsername(localStorage.getItem("username") || "")
    }, [])
    

    const navigate = useNavigate()

    function handleLogout(e) {
        e.preventDefault()

        localStorage.setItem("is_authenticated", "false")
        localStorage.setItem("username", "")
        localStorage.setItem("userId", "")
        setIsAuthenticated(false)
        setUsername("")
        navigate("/")
    }

  return (
    <>
     {!isAuthenticated ? (
        <div className="not-authed-container">
            <a href="/login">Login</a>
            <a href="/signup">SignUp</a>
        </div>
     ) : (
        <div className='authed-container'>
            <p>{username}</p>
            <button onClick={handleLogout}>Log Out</button>
        </div>
     )}
     <Video videoId={6}/> 
    </>
  )
}
