# Trivia API Documentation

## Base URL

Local development: http://localhost:5000

### Error Handling

Errors are returned as JSON objects in the following format:

```json
{
  "success": false,
  "error": 400,
  "message": "Bad request"
}
```

### The API will return these error types when requests fail:

1. 400: Bad Request
2. 404: Resource Not Found
3. 422: Unprocessable Entity
4. 500: Internal Server Error

## Endpoints

### GET /categories

#### Fetches a dictionary of all available categories

#### Request Arguments: None

#### Returns:

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

### GET /questions

#### Fetches paginated questions

#### Returns:

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "Sample question",
      "answer": "Sample answer",
      "category": 1,
      "difficulty": 3
    }
  ],
  "total_questions": 20,
  "categories": {
    "1": "Science",
    "2": "Art"
  }
}
```

### DELETE /questions/<question_id>

#### Deletes specified question

#### Request Arguments:

| Parameter   | Type    | Required | Default | Description            |
| ----------- | ------- | -------- | ------- | ---------------------- |
| question_id | integer | Yes      | N.A     | The id of the question |

#### Returns:

```json
{
  "success": true,
  "deleted": 1
}
```

### POST /questions

#### Creates new question

#### Request Body:

```json
{
  "question": "New question",
  "answer": "New answer",
  "category": 1,
  "difficulty": 3
}
```

#### Returns:

```json
{
  "success": true,
  "created": 1
}
```

### POST /questions/search

#### Searches questions by term

#### Request Body:

```json
{
  "searchTerm": "title"
}
```

#### Returns:

```json
{
  "success": true,
  "questions": [],
  "total_questions": 0
}
```

### GET /categories/<category_id>/questions

#### Fetches questions by category

#### Request Arguments:

| Parameter   | Type    | Required | Default | Description            |
| ----------- | ------- | -------- | ------- | ---------------------- |
| category_id | integer | yes      | N.A     | The id of the category |

#### Returns:

```json
{
  "success": true,
  "questions": [],
  "total_questions": 0,
  "current_category": 1
}
```

### POST /quizzes

#### Fetches random questions for quiz

#### Request Body:

```json
{
  "previous_questions": [],
  "quiz_category": {
    "id": 1,
    "type": "Science"
  }
}
```

#### Returns:

```json
{
  "success": true,
  "question": {
    "id": 1,
    "question": "Sample question",
    "answer": "Sample answer",
    "category": 1,
    "difficulty": 3
  }
}
```
