import express from 'express'
const app = express()
const PORT = 3002
app.use(express.json())
app.get('/', (req, res) => {
  res.send('Hello World!')
})
app.listen(PORT, () => {
  //console.log(`Server is listening on port ${PORT}`)
})
