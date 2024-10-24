import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./notifications.css";

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await axios.get("http://localhost:5000/notifications");
        setNotifications(response.data.notifications);
      } catch (err) {
        if (
          err.response &&
          (err.response.status === 401 || err.response.status === 403)
        ) {
          navigate("/signin");
        } else {
          setError("Error fetching notifications.");
        }
      }
    };

    fetchNotifications();
  }, [navigate]);

  const markNotificationsSeen = async () => {
    try {
      await axios.post("http://localhost:5000/notifications/mark_seen");
      setNotifications([]); // Clear notifications after marking them as seen
    } catch (err) {
      setError("Error marking notifications as seen.");
    }
  };

  return (
    <div className="notifications-page">
      <h1>Notifications</h1>
      {notifications.length > 0 ? (
        <ul className="notifications-list">
          {notifications.map((notification, index) => (
            <li key={index}>
              {notification.message} -{" "}
              {new Date(
                new Date(notification.timestamp).setHours(
                  new Date(notification.timestamp).getHours() - 6
                )
              ).toLocaleString()}
            </li>
          ))}
        </ul>
      ) : (
        <p>No new notifications</p>
      )}
      {notifications.length > 0 && (
        <button onClick={markNotificationsSeen}>Mark all as seen</button>
      )}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default Notifications;
