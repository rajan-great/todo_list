from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection, init_db
import mysql.connector

app = Flask(__name__)
CORS(app)

init_db()

@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        todos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for todo in todos:
            todo['completed'] = bool(todo['completed'])
        
        return jsonify(todos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    
    if not title:
        return jsonify({'error': 'Title cannot be empty'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO todos (title, description) VALUES (%s, %s)",
            (title, description)
        )
        conn.commit()
        todo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({'id': todo_id, 'title': title, 'description': description, 'completed': False}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM todos WHERE id = %s", (todo_id,))
        todo = cursor.fetchone()
        
        if not todo:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Todo not found'}), 404
        
        title = data.get('title', todo['title'])
        description = data.get('description', todo['description'])
        completed = data.get('completed', todo['completed'])
        
        cursor.execute(
            "UPDATE todos SET title = %s, description = %s, completed = %s WHERE id = %s",
            (title, description, completed, todo_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': todo_id,
            'title': title,
            'description': description,
            'completed': bool(completed)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Todo not found'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Todo deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

