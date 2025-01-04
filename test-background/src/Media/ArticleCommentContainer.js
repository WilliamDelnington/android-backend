import React, { useEffect, useState } from 'react'
import ArticleComment from './ArticleComment'

export default function ArticleCommentContainer({ articleId }) {
    const [errorMessage, setErrorMessage] = useState("")
    const [loading, setLoading] = useState(true)
    const [commentData, setCommentData] = useState([])
    const publicUrl = "https://android-backend-tech-c52e01da23ae.herokuapp.com/"
    const privateUrl = "http://192.168.56.1:8000/"

    useEffect(() => {
        async function fetchData() {
            try {
                const res = await fetch(privateUrl + `articles/comments/temporary/search?articleId=${articleId}`)
                if (!res.ok) {
                    throw new Error(`${res.status}`)
                }
                const data = await res.json()
                const commentdata = await Promise.all(data.map(d => getUsername(d)))
                setCommentData(commentdata)
            } catch (error) {
                setErrorMessage(`Error fetching comments in video ${articleId}: ${error.message}`)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    async function getUsername(data) {
        const user = data.user

        return await fetch(privateUrl + `users/temporary/${user}`).then(res => {
            if (!res.ok) {
                setErrorMessage(`Error getting username from ${user}: ${res.status}`)
            }
            return res.json()
        }).then(d => {
            const username = d.username

            console.log({...data, username: username})
            return {...data, username: username}
        }).catch(err => {
            setErrorMessage(`Error getting username from ${user}: ${err.message}`)
        })
    }



  return (
      <div>
          {loading && <div>Loading comments...</div>}
          <div className="comment-container">
              {(!loading && commentData.length > 0) ? commentData.map((comment, key) => (
                  <ArticleComment
                  key={key}
                  commentId={comment.id}
                  content={comment.content} 
                  username={comment.username} 
                  createdTime={comment.createdTime}
                  articleId={articleId}/>
              )) : <div></div>}
          </div>
          <div style={{
              color: "red"
          }}>{errorMessage}</div>
      </div>
    )
}
