import React, { useEffect, useState } from 'react'
import { Button, Form } from 'react-bootstrap'
import { useNavigate, useParams } from 'react-router'
import ArticleCommentContainer from './ArticleCommentContainer'

export default function Article() {
    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/"
    const privateUrl = "http://192.168.56.1:8000/"

    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [username, setUsername] = useState("")

    const navigate = useNavigate()

    const { articleId } = useParams()

    if (!articleId) {
        throw new Error("No id were specified.")
    }

    const [errorMessage, setErrorMessage] = useState("")
    const [articleLoading, setArticleLoading] = useState(true)
    const [articleData, setArticleData] = useState({})

    const [comment, setComment] = useState("")
    const [replyLoading, setReplyLoading] = useState(false)
    const [isArticleLiked, setIsArticleLiked] = useState(false)
    const [likeUnlikeLoading, setLikeUnlikeLoading] = useState(false)

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
        async function fetchArticleData() {
            try {
                const response = await fetch(privateUrl + `articles/${articleId}`)
                if (!response.ok) {
                    throw new Error(response.status)
                }
                const data = await response.json()
                setArticleData({
                    ...articleData,
                    articleBrandType: data.articleBrandType,
                    sourceName: data.sourceName,
                    author: data.author,
                    title: data.title,
                    description: data.description,
                    urlToImage: data.urlToImage,
                    publishedAt: data.publishedAt,
                    content: data.content,
                    commentNum: data.commentNum,
                    likeNum: data.likeNum
                })

                console.log(data.content)
            } catch (err) {
                setErrorMessage("Error fetching article data: " + err.message)
            } finally {
                setArticleLoading(false)
            }
        }

        fetchArticleData()
    }, [])

    useEffect(() => {
        setErrorMessage("")
        async function getReaction() {
            try {
                const res = await fetch(privateUrl + `articles/reactions/temporary/search?videoId=${articleId}&user=${localStorage.getItem("userId")}`)
                if (!res.ok) {
                    throw new Error(`${res.status}`)
                }
                const data = await res.json()
                console.log(data)
                if (data.length === 0) {
                    setIsArticleLiked(false)
                } else {
                    setIsArticleLiked(true)
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
            const response = await fetch(privateUrl + "articles/comments/temporary", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user: parseInt(localStorage.getItem("userId")),
                    articleId: articleId,
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
           const response = await fetch(privateUrl + "articles/reactions/temporary", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user: parseInt(localStorage.getItem("userId")),
                    articleId: articleId,
                })
            })
            if (response.status < 200 || response.status >= 300) {
                throw new Error(response.status)
            }
            console.log(await response.json())
            setIsArticleLiked(true)
        } catch (err) {
            setErrorMessage("Error liking article: " + err.message)
        } finally {
            setLikeUnlikeLoading(false)
        }
    }

    async function unlikeVideo(e) {
        e.preventDefault()
        setLikeUnlikeLoading(true)

        try {
            const response = await fetch(
                privateUrl + `articles/reactions/temporary/search?videoId=${articleId}&user=${localStorage.getItem("userId")}`,
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
            setIsArticleLiked(false)
        } catch (err) {
            setErrorMessage("Error unliking article: " + err.message)
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
        <div style={{color:"red"}}>{errorMessage}</div>
        {articleLoading && <div>Loading Article...</div>}
        <article>
            <h4 className='article-type'>Article Type: {articleData.articleBrandType}</h4>

            <h4 className='article-source'>From: {articleData.sourceName}</h4>

            <h1 className='article-title'>{articleData.title}</h1>

            <p>By <span className='article-author' style={{fontWeight: 500}}>{articleData.author}</span></p>

            <p>Published At: <time dateTime={articleData.publishedAt}>{articleData.publishedAt}</time></p>

            <h2 className='article-description'>{articleData.description}</h2>

            {articleData.urlToImage && <img src={articleData.urlToImage}></img>}

            {articleData.content ? articleData.content.split("\n").map((co, key) => (
                <p key={key}>{co}</p>
            )) : <div></div>}
        </article>
        <div className="decision-container">
            <Button disabled={(isArticleLiked || likeUnlikeLoading || !isAuthenticated)} onClick={likeVideo}>Like Article</Button>
            <Button disabled={(!isArticleLiked || likeUnlikeLoading || !isAuthenticated)} onClick={unlikeVideo}>Unlike Article</Button>
        </div>
        <div className='article-info-container'>
            <p>Likes: {articleData.likeNum}</p>
            <p>Comments: {articleData.commentNum}</p>
        </div>
        <div className='article-comments-container'>
            <Form method='post' onSubmit={addComment} style={
                isAuthenticated
                ? {display: 'block'}
                : {display: 'none'}}>
                <Form.Label>Add Comment: </Form.Label>
                <Form.Control 
                type='text'
                name="comment_content"
                value={comment}
                onChange={e => setComment(e.target.value)}/>
                <Button type='submit'>Add Comment</Button>
            </Form>
            {replyLoading && <div>Replying...</div>}
            <ArticleCommentContainer articleId={articleId} />
        </div>
    </>
  )
}
