import React, { useState } from 'react'
import { Button, Form } from 'react-bootstrap'

export default function VideoComment({content, username, createdTime}) {
    const [message, setMessage] = useState("")

    function handleSubmit(e) {

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
            onChange={setMessage} />
            <Button type="submit">Reply</Button>
        </Form>
    </div>
  )
}
