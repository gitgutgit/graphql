from flask import Flask
from flask_graphql import GraphQLView
from graphene import ObjectType, String, Int, List, Schema, Float
import requests
# Initialize Flask app
app = Flask(__name__)

# Define GraphQL types
class ChunkResult(ObjectType):
    chunkId = Int()
    contentId = Int()
    fileName = String()
    text = String()
    similarityScore = Float()

class Query(ObjectType):
    searchSimilarChunks = List(
        ChunkResult,
        userId=String(required=True),
        query=String(required=True),
        limit=Int(default_value=5)
    )

    def resolve_searchSimilarChunks(parent, info, userId, query, limit):
        print(f"Received request: userId={userId}, query={query}, limit={limit}")
        try:
            response = requests.get(
                "http://34.207.126.237/api/search",
                params={"user_id": userId, "query": query, "limit": limit}
            )
            print(f"API Response: {response.json()}")
            response.raise_for_status()
            results = response.json().get("results", [])
            return [
                {
                    "chunkId": result["chunk_id"],
                    "contentId": result["content_id"],
                    "fileName": result["file_name"],
                    "text": result["text"],
                    "similarityScore": result["similarity_score"]
                }
                for result in results
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return []


# Create schema
schema = Schema(query=Query)

# Add GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

# Add a health check route
@app.route("/")
def index():
    return "GraphQL API is running!"
# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
