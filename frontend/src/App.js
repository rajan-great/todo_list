import React, { useState, useEffect } from 'react';
import './App.css';
import TodoList from './components/TodoList';
import AddTodo from './components/AddTodo';
import { getTodos, createTodo, updateTodo, deleteTodo } from './services/api';

function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      setLoading(true);
      const data = await getTodos();
      setTodos(data);
      setError(null);
    } catch (err) {
      setError('Failed to load todos. Make sure the backend is running.');
      console.error('Error fetching todos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTodo = async (title, description) => {
    try {
      const newTodo = await createTodo(title, description);
      setTodos([newTodo, ...todos]);
    } catch (err) {
      setError('Failed to add todo');
      console.error('Error adding todo:', err);
    }
  };

  const handleToggleComplete = async (id, completed) => {
    try {
      const todo = todos.find(t => t.id === id);
      if (!todo) return;
      
      const updated = await updateTodo(id, {
        ...todo,
        completed: !completed
      });
      
      setTodos(todos.map(t => t.id === id ? updated : t));
    } catch (err) {
      setError('Failed to update todo');
      console.error('Error updating todo:', err);
    }
  };

  const handleDeleteTodo = async (id) => {
    try {
      await deleteTodo(id);
      setTodos(todos.filter(t => t.id !== id));
    } catch (err) {
      setError('Failed to delete todo');
      console.error('Error deleting todo:', err);
    }
  };

  const handleUpdateTodo = async (id, title, description) => {
    try {
      const todo = todos.find(t => t.id === id);
      if (!todo) return;
      
      const updated = await updateTodo(id, {
        ...todo,
        title,
        description
      });
      
      setTodos(todos.map(t => t.id === id ? updated : t));
    } catch (err) {
      setError('Failed to update todo');
      console.error('Error updating todo:', err);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>My Todo List</h1>
        
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}
        
        <AddTodo onAdd={handleAddTodo} />
        
        {loading ? (
          <div className="loading">Loading todos...</div>
        ) : (
          <TodoList
            todos={todos}
            onToggleComplete={handleToggleComplete}
            onDelete={handleDeleteTodo}
            onUpdate={handleUpdateTodo}
          />
        )}
      </div>
    </div>
  );
}

export default App;

