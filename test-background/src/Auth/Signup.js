import React, { useState } from 'react'
import {Button, Form} from 'react-bootstrap'
import {useNavigate} from 'react-router-dom'

export default function Signup() {
    const [errorMessage, setErrorMessage] = useState("")
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [retypePassword, setRetypePassword] = useState("")

    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/signup"
    const privateUrl = "http://192.168.56.1:8000/signup"

    const navigate = useNavigate()

    function handleSubmit(e) {
        let success = true
        setErrorMessage("")
        e.preventDefault()

        fetch(publicUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                confirm_password: retypePassword
            })
        }).then(response => {
            if (response.status < 200 || response.status >= 300) {
                setErrorMessage(`Error sign up ${username}: ${response.status}`)
                success = false
            }
            return response.json()
        }).then(data => {
            if (data == null) return
            localStorage.setItem("is_authenticated", "true")
            localStorage.setItem("username", username)
            console.log(data)
            if (success) {navigate("/")}
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
                onChange={e => setUsername(e.target.value)} />
            </Form.Group>
            <Form.Group>
                <Form.Label>Enter your email:</Form.Label>
                <Form.Control 
                type='email'
                name="email"
                placeholder="Email"
                value={email}
                onChange={e => setEmail(e.target.value)} />
            </Form.Group>
            <Form.Group>
                <Form.Label>Enter your password: </Form.Label>
                <Form.Control 
                type='password'
                name="password"
                placeholder='Password'
                value={password}
                onChange={e => setPassword(e.target.value)}/>
            </Form.Group>
            <Form.Group>
                <Form.Label>Reenter password: </Form.Label>
                <Form.Control 
                type='password'
                name="confirm_password"
                placeholder='password'
                value={retypePassword}
                onChange={e => setRetypePassword(e.target.value)}/>
            </Form.Group>
            <Button type="submit" variant='primary'>Sign Up</Button>
        </Form>
        <div style={{
            color: "red"
        }}>{errorMessage}</div>
    </>
  )
}
