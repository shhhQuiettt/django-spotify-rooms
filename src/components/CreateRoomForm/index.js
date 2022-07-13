import React from "react";
import "./index.css";
import { useForm } from "react-hook-form";
import { createRoom } from "../../service";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const CreateRoomForm = () => {
  let navigate = useNavigate();
  useEffect(() => {
    if (localStorage.hasOwnProperty("roomCode")) {
      navigate("../room", { replace: true });
    }
  }, []);

  const { register, handleSubmit } = useForm();

  const [error, setError] = useState(null);
  const onSubmit = async (data) => {
    data = { ...data, user_can_pause: data.user_can_pause == "true" };
    let err = await createRoom(data);
    err?.message ? setError(err.message) : navigate("/room");
  };

  return (
    <form
      className="create-room-form"
      onSubmit={handleSubmit(onSubmit)}
      data-testid="create-room-form"
    >
      <h2 className="form-title">Create room</h2>
      <div className="input-wrapper">
        <label htmlFor="votes-to-skip">
          Votes to skip:
          <input
            type="number"
            id="votes-to-skip"
            className="narrow-input"
            defaultValue={3}
            {...register("votes_to_skip", {
              valueAsNumber: true,
              required: true,
              min: 1,
            })}
          />
        </label>
      </div>

      <h3 className="main-label">Guests:</h3>
      <div className="input-wrapper">
        <label htmlFor="can-pause" className="radio-container">
          Can pause
          <input
            type="radio"
            id="can-pause"
            value={true}
            {...register("user_can_pause", { required: true })}
            defaultChecked
          />
          <span className="checkmark"></span>
        </label>
        <label htmlFor="no-control" className="radio-container">
          No control
          <input
            type="radio"
            id="no-control"
            value={false}
            {...register("user_can_pause", { required: true })}
          />
          <span className="checkmark"></span>
        </label>
      </div>
      <button type="submit" data-testid="create-button">
        Create
      </button>
      {error && <div className="error-field">{error}</div>}
    </form>
  );
};

export default CreateRoomForm;
