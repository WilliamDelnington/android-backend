import React, { useState } from 'react'
import {Button, Form} from 'react-bootstrap'
import {useNavigate} from 'react-router-dom'

export default function Login() {
    const [errorMessage, setErrorMessage] = useState("")
    const [username, setUsername] = useState("")

    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/users/temporary"
    const privateUrl = "http://192.168.56.1:8000/users/temporary"

    const navigate = useNavigate()

    function handleSumbit(e) {

        e.preventDefault()

        const query = `/search?username=${username}`

        fetch(privateUrl + query).then(response => {
            if (!response.ok) {
                setErrorMessage(`Error getting content from ${username}: ${response.status}`)
            }
            return response.json()
        }).then(data => {
            localStorage.setItem("is_authenticated", true)
            localStorage.setItem("username", username)
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
                <Form.Label>Enter your username: </Form.Label>
                <Form.Control
                type='text'
                name="username"
                placeholder='Your username'
                value={username}
                onChange={setUsername} />
            </Form.Group>
            <Button type="submit" variant="primary">Login</Button>
        </Form>
        <div style={{
            color: "red"
        }}>{errorMessage}</div>
    </>
  )
}
