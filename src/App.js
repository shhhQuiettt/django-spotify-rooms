import Player from "./components/Player";
import CreateRoomForm from "./components/CreateRoomForm";
import "./index.css";
import JoinRoomForm from "./components/JoinRoomForm";
import { Routes, Route, Link } from "react-router-dom";
import Room from "./components/Room";
import NavButtons from "./components/NavButtons";
import Header from "./components/Header";

import { useState } from "react";

function App() {
  const [roomCode, setRoomCode] = useState(localStorage.getItem("roomCode"));
  return (
    <div className="App">
      <Header />
      <Routes>
        <Route path="/" element={<NavButtons />} />
        <Route path="/room" element={<Room code={roomCode} />} />
        <Route path="/room/join" element={<JoinRoomForm />} />
        <Route path="/room/create" element={<CreateRoomForm />} />
      </Routes>
    </div>
  );
}

export default App;
