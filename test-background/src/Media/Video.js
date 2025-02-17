import React, { useEffect, useState } from 'react'
import { Button, Form } from 'react-bootstrap'
import VideoCommentContainer from './VideoCommentContainer'
import { useParams, useNavigate } from 'react-router-dom'

export default function Video() {
    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/"
    const privateUrl = "http://192.168.56.1:8000/"

    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [username, setUsername] = useState("")

    const navigate = useNavigate()

    const { videoId } = useParams()

    const [videoSource, setVideoSource] = useState("")
    const [errorMessage, setErrorMessage] = useState("")
    const [comment, setComment] = useState("")
    const [loading, setLoading] = useState(true)
    const [replyLoading, setReplyLoading] = useState(false)
    const [isVideoLiked, setIsVideoLiked] = useState(false)
    const [likeUnlikeLoading, setLikeUnlikeLoading] = useState(false)
    const [videoInfo, setVideoInfo] = useState({
        url: "",
        fetchable_url: "",
        thumbnailImageUrl: "",
        createdTime: "",
        likeNum: 0,
        commentNum: 0
    })

    useEffect(() => {
        setIsAuthenticated(localStorage.getItem("is_authenticated") === "true")
        setUsername(localStorage.getItem("username") || "")
    }, [])

    function handleLogout(e) {
        e.preventDefault()

        localStorage.setItem("is_authenticated", "false")
        localStorage.setItem("username", "")
        localStorage.setItem("userId", "")
        setIsAuthenticated(false)
        setUsername("")
        navigate("/")
    }

    useEffect(() => {
        setErrorMessage("")
        async function fetchData() {
            try {
                const res = await fetch(privateUrl + `videos/${videoId}`)
                if (!res.ok) {
                    throw new Error(`${res.status}`)
                }
                const data = await res.json()
                setVideoInfo({
                    ...videoInfo,
                    fetchable_url: data.fetchable_url,
                    thumbnailImageUrl: data.thumbnailImageUrl,
                    createdTime: data.createdTime,
                    likeNum: data.likeNum,
                    commentNum: data.commentNum
                })

                setVideoSource(privateUrl + data.fetchable_url)
            } catch (err) {
                setErrorMessage(`Error fetching video ${videoId}: ${err.message}`)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    useEffect(() => {
        setErrorMessage("")
        async function getReaction() {
            try {
                const res = await fetch(privateUrl + `videos/reactions/temporary/search?videoId=${videoId}&user=${localStorage.getItem("userId")}`)
                if (!res.ok) {
                    throw new Error(`${res.status}`)
                }
                const data = await res.json()
                console.log(data)
                if (data.length === 0) {
                    setIsVideoLiked(false)
                } else {
                    setIsVideoLiked(true)
                }
            } catch (err) {
                setErrorMessage("Error getting reaction: " + err.message)
            }
        }

        getReaction()
    })

    async function addComment(e) {
        e.preventDefault()
        setReplyLoading(true)

        try {
            const response = await fetch(privateUrl + "videos/comments/temporary", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user: parseInt(localStorage.getItem("userId")),
                    videoId: videoId,
                    parentId: null,
                    content: comment
                })
            })
            if (response.status < 200 || response.status >= 300) {
                throw new Error(response.status)
            }
            console.log(await response.json())
        } catch (error) {
            setErrorMessage(`Error adding comment: ${error.message}`)
        } finally {
            setReplyLoading(false)
        }
    }

    async function likeVideo(e) {
        e.preventDefault()
        setLikeUnlikeLoading(true)

        try {
           const response = await fetch(privateUrl + "videos/reactions/temporary", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user: parseInt(localStorage.getItem("userId")),
                    videoId: videoId,
                })
            })
            if (response.status < 200 || response.status >= 300) {
                throw new Error(response.status)
            }
            console.log(await response.json())
            setIsVideoLiked(true)
        } catch (err) {
            setErrorMessage("Error liking video: " + err.message)
        } finally {
            setLikeUnlikeLoading(false)
        }
    }

    async function unlikeVideo(e) {
        e.preventDefault()
        setLikeUnlikeLoading(true)

        try {
            const response = await fetch(
                privateUrl + `videos/reactions/temporary/search?videoId=${videoId}&user=${localStorage.getItem("userId")}`,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
            if (response.status < 200 || response.status >= 300) {
                throw new Error(response.status)
            }
            console.log(await response.json())
            setIsVideoLiked(false)
        } catch (err) {
            setErrorMessage("Error unliking video: " + err.message)
        } finally {
            setLikeUnlikeLoading(false)
        }
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
        <div style={{color: "red"}}>{errorMessage}</div>
        {loading && <div>Currently Loading...</div>}
        <video width={400} height={210} controls>
            {videoSource ? <source src={videoSource} type='video/mp4'/> : <div>Loading...</div>}
        </video>
        <div className="decision-container">
            <Button disabled={(isVideoLiked || likeUnlikeLoading || !isAuthenticated)} onClick={likeVideo}>Like Video</Button>
            <Button disabled={(!isVideoLiked || likeUnlikeLoading || !isAuthenticated)} onClick={unlikeVideo}>Unlike Video</Button>
        </div>
        <div className="video-info-container">
            <p>Likes: {videoInfo.likeNum}</p>
            <p>Comments: {videoInfo.commentNum}</p>
        </div>
        <div className="video-comments-container">
            <Form method="POST" onSubmit={addComment} style={
                isAuthenticated
                ? {display: 'block'}
                : {display: 'none'}}>
                <Form.Label>Add Comment: </Form.Label>
                <Form.Control 
                type='text'
                name="comment_content"
                value={comment}
                onChange={e => setComment(e.target.value)}/>
                <Button type="submit">Add Comment</Button>
            </Form>
            {replyLoading && <div>Replying...</div>}
            <VideoCommentContainer videoId={videoId} />
        </div>
    </>
  )
}
