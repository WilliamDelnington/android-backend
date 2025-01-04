import React, {useEffect, useState} from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Form } from 'react-bootstrap'

export default function Main() {
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [username, setUsername] = useState("")
    const [videoId, setVideoId] = useState(1)
    const [articleId, setArticleId] = useState(1)

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

    function goToArticle(e) {
        e.preventDefault()
        navigate(`/article/${articleId}`)
    }

    function goToVideo(e) {
        e.preventDefault()
        navigate(`/video/${videoId}`)
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
    <Form onSubmit={goToArticle}>
        <Form.Label>Enter Article Id (number): </Form.Label>
        <Form.Control 
        type='number'
        name="articleId"
        value={articleId}
        onChange={e => setArticleId(e.target.value)}/>
        <Button type="submit">Go to article</Button>
    </Form>
    <Form onSubmit={goToVideo}>
        <Form.Label>Enter Video Id (number): </Form.Label>
        <Form.Control 
        type='number'
        name="videoId"
        value={videoId}
        onChange={e => setVideoId(e.target.value)}/>
        <Button type='submit'>Go to video</Button>
    </Form>
    </>
  )
}
