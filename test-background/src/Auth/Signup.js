import React, { useState } from 'react'
import {Button, Form} from 'react-bootstrap'
import {useNavigate} from 'react-router-dom'

export default function Signup() {
    const [errorMessage, setErrorMessage] = useState("")
    const [username, setUsername] = useState("")

    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/users/temporary"
    const privateUrl = "http://192.168.56.1:8000/users/temporary"

    const navigate = useNavigate()

    function handleSubmit(e) {
        setErrorMessage("")
        e.preventDefault()

        fetch(privateUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username
            })
        }).then(response => {
            if (response.status < 200 || response.status >= 300) {
                setErrorMessage(`Error sign up ${username}: ${response.status}`)
            }
            return response.json()
        }).then(data => {
            localStorage.setItem("is_authenticated", true)
            localStorage.setItem("username", username)
            localStorage.setItem("userId", data.id)
            navigate("/")
        }).catch(error => {
            setErrorMessage(`Error requesting: ${error.message}`)
        })
    }

  return (
    <>
        <h2>Sign Up</h2>
        <Form method="post" onSubmit={handleSubmit}>
            <Form.Group>
                <Form.Label>Enter your username:</Form.Label>
                <Form.Control
                type="text"
                name="username"
                placeholder="Your username"
                value={username}
                onChange={setUsername}></Form.Control>
            </Form.Group>
            <Button type="submit" variant='primary'>Sign Up</Button>
        </Form>
        <div style={{
            color: "red"
        }}>{errorMessage}</div>
    </>
  )
}
