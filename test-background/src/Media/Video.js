import React, { useEffect, useState } from 'react'
import { Button, Form } from 'react-bootstrap'
import VideoCommentContainer from './VideoCommentContainer'

export default function Video({ videoId }) {
    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/"
    const privateUrl = "http://192.168.56.1:8000/"

    const [videoSource, setVideoSource] = useState("")
    const [errorMessage, setErrorMessage] = useState("")
    const [comment, setComment] = useState("")
    const [loading, setLoading] = useState(true)
    const [videoInfo, setVideoInfo] = useState({
        url: "",
        fetchable_url: "",
        thumbnailImageUrl: "",
        createdTime: "",
        likeNum: 0,
        commentNum: 0
    })

    // fetch(privateUrl + `videos/${videoId}`).then(response => {
    //     if (!response.ok) {
    //         setErrorMessage(`Error fetching video ${videoId}: ${response.status}`)
    //     }
    //     return response.json()
    // }).then(data => {
    //     setVideoInfo({
    //         ...videoInfo,
    //         fetchable_url: data.fetchable_url,
    //         thumbnailImageUrl: data.thumbnailImageUrl,
    //         createdTime: data.createdTime,
    //         likeNum: data.likeNum,
    //         commentNum: data.commentNum
    //     })

    //     setVideoSource(null)
    // }).catch(err => {
    //     setErrorMessage(`Error fetching video ${videoId}: ${err.message}`)
    //     console.error(err)
    // })

    useEffect(() => {
        setErrorMessage("")
        async function fetchData() {
            try {
                const res = await fetch(privateUrl + `videos/${videoId}`)
                if (!res.ok) {
                    throw new Error(`${res.status}`)
                }
                const data = await res.json()
                console.log(data)
                setVideoInfo({
                    ...videoInfo,
                    fetchable_url: data.fetchable_url,
                    thumbnailImageUrl: data.thumbnailImageUrl,
                    createdTime: data.createdTime,
                    likeNum: data.likeNum,
                    commentNum: data.commentNum
                })

                console.log(privateUrl + data.fetchable_url)
                setVideoSource(privateUrl + data.fetchable_url)
            } catch (err) {
                setErrorMessage(`Error fetching video ${videoId}: ${err.message}`)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    function addComment(e) {
        e.preventDefault()

        
    }

  return (
    <>
        {loading && <div>Currently Loading...</div>}
        <video width={400} height={210} controls>
            {videoSource ? <source src={videoSource} type='video/mp4'/> : <div>Loading...</div>}
        </video>
        <div className="video-info-container">
            <p>Likes: {videoInfo.likeNum}</p>
            <p>Comments: {videoInfo.commentNum}</p>
        </div>
        <div className="video-comments-container">
            <div style={{
                color: "red"
            }}>{errorMessage}</div>
            <Form method="POST">
                <Form.Label>Add Comment: </Form.Label>
                <Form.Control 
                type='text'
                name="comment_content"
                value={comment}
                onChange={setComment}/>
                <Button type="submit">Add Comment</Button>
            </Form>
            <VideoCommentContainer videoId={videoId} />
        </div>
    </>
  )
}
