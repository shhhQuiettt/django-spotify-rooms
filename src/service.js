import axios from "axios";

export const createRoom = async (roomData) => {
  try {
    const response = await axios.post("/api/room/create", roomData);
    localStorage.setItem("roomCode", response.data.code);
    return null;
  } catch (error) {
    console.log(error);
    return error;
  }
};

export const joinRoom = async (roomCode) => {
  try {
    const response = await axios.get("/api/room/" + roomCode);
    localStorage.setItem("roomCode", response.data.code);
    return null;
  } catch (error) {
    return error;
  }
};

export const getTrack = async () => {
  try {
    const response = await axios.get("/spotify/track/current");
    return [response.data, null];
  } catch (error) {
    return [null, error];
  }
};
