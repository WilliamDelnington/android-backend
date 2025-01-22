import React, { useState } from 'react'
import {Button, Form} from 'react-bootstrap'
import {Link, useNavigate} from 'react-router-dom'

export default function Login() {
    const [errorMessage, setErrorMessage] = useState("")
    const [password, setPassword] = useState("")
    const [email, setEmail] = useState("")

    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/users"
    const privateUrl = "http://192.168.56.1:8000/login"

    const navigate = useNavigate()

    function handleSumbit(e) {

        e.preventDefault()

        fetch(privateUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                email: email,
                password: password
            })
        }).then(response => {
            if (!response.ok) {
                setErrorMessage(`Error getting content from ${email}: ${response.status}`)
                throw new Error(`Error getting content from ${email}: ${response.status}`)
            }
            return response.json()
        }).then(data => {
            localStorage.setItem("is_authenticated", "true")
            localStorage.setItem("email", email)
            localStorage.setItem("userId", data.id)
            navigate("/")
        }).catch(error => {
            setErrorMessage(`Error: ${error.message}`)
        })
    }

  return (
    <>
        <h2>Login</h2>
        <Form method="post" onSubmit={handleSumbit}>
            <Form.Group>
                <Form.Label>Enter your email: </Form.Label>
                <Form.Control
                type='text'
                name="email"
                placeholder='email'
                value={email}
                onChange={e => setEmail(e.target.value)} />
            </Form.Group>
            <Form.Group>
                <Form.Label>Enter your password: </Form.Label>
                <Form.Control 
                type='password'
                placeholder='password'
                value={password}
                onChange={e => setPassword(e.target.value)} />
            </Form.Group>
            <Button type="submit" variant="primary">Login</Button>
            <Button as={Link} to="/forgotPassword">Forgot Password?</Button>
        </Form>
        <div style={{
            color: "red"
        }}>{errorMessage}</div>
    </>
  )
}
