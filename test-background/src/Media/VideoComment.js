import React, { useState } from 'react'
import { Button, Form } from 'react-bootstrap'

export default function VideoComment({userId, content, username, createdTime, videoId, commentId}) {
    const [message, setMessage] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/"
    const privateUrl = "http://192.168.56.1:8000/"

    async function handleSubmit(e) {
      setError("")
      setLoading(true)
      e.preventDefault()
      
      try {
        const response = await fetch(privateUrl + "videos/comments/temporary", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            content: message,
            videoId: videoId,
            user: localStorage.getItem("userId"),
            parentId: commentId
          })
        })
        if (response.status < 200 || response.status >= 300) {
          throw new Error("response returning the status " + response.status)
        }
      } catch (err) {
        setError("Error creating comment: " + err.message)
      } finally {
        setLoading(false)
      }
      
    }

  return (
    <div className="video-comment">
        <div className="username">{username}</div>
        <div className="content">{content}</div>
        <div className="createdTime">{createdTime}</div>
        <Form method="POST" onSubmit={handleSubmit}>
            <Form.Control 
            type="text"
            placeholder='Reply...'
            value={message}
            onChange={e => setMessage(e.target.value)} />
            <Button type="submit">Reply</Button>
        </Form>
        {loading && <div className="loading">Requesting...</div>}
        <div style={{
          color: "red"
        }}>{error}</div>
    </div>
  )
}
