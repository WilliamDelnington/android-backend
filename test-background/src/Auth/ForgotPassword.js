import React, { useState } from 'react'
import { Button, Form } from 'react-bootstrap'

export default function ForgotPassword() {
    const [email, setEmail] = useState("")
    const [errorMessage, setErrorMessage] = useState("")
    const [completeMessage, setCompleteMessage] = useState("")

    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/password-reset"
    const privateUrl = "http://192.168.56.1:8000/password-reset"

    function handleSubmit(e) {
        e.preventDefault()

        // const query = `/search?email=${email}`

        fetch(publicUrl, {
            method: 'POST',
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify({ email: email })
        }).then(response => {
            if (!response.ok) {
                setErrorMessage(`Error sending password for email ${email}: ${response.status}`)
            }
            return response.json()
        }).then((data) => {
            console.log(data)
            setCompleteMessage("Email has sent to reset email.")
        }).catch(error => {
            setErrorMessage(`Error sending password for email ${email}: ${error.message}`)
        })
    }

  return (
    <>
        <div>Enter your email:</div>
        <Form onSubmit={handleSubmit} method="post">
            <Form.Group>
                <Form.Label>Email:</Form.Label>
                <Form.Control
                type='text'
                value={email}
                onChange={e => setEmail(e.target.value)}/>
            </Form.Group>
            <Button type='submit' variant='primary'>Send Email</Button>
        </Form>
        <div style={{color: "red"}}>{errorMessage}</div>
        <div style={{color: "green"}}>{completeMessage}</div>
    </>
  )
}
