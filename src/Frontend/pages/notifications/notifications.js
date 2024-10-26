import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Icon from "../../templates/icon";
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

  const handleNotificationClick = (postId) => {
    navigate(`/post/${postId}`);
  };

  return (
    <div className="notifications-page">
      <Icon />
      <h1>Notifications</h1>
      {notifications.length > 0 ? (
        <ul className="notifications-list">
          {notifications.map((notification, index) => (
            <li
              key={index}
              onClick={() => handleNotificationClick(notification.post_id)}
              className="notification-item"
            >
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
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default Notifications;
