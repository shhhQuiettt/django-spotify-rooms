import React, { useRef, useState, useEffect } from "react";
import "./index.css";
import { FaPlay, FaPause } from "react-icons/fa";
import { BsFillSkipEndFill, BsFillSkipStartFill } from "react-icons/bs";
import { getTrack, voteToSkip, playTrack, pauseTrack } from "../../service";

const Player = () => {
  const [currentTrack, setCurrentTrack] = useState({ "current-votes": 0 });

  const [votesToSkip, setVoteToSkip] = useState(
    localStorage.getItem("votesToSkip")
  );

  const [error, setError] = useState(null);
  const refreshTrack = async () => {
    const [track, err] = await getTrack();
    err?.message ? setError(err.message) : setCurrentTrack(track);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      refreshTrack();
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  });

  // TODO: There MUST be a better way of doing this, this is so retardet
  //This prevents calling slideTextField useRef hook,
  //before component (and DOM node) was rendered
  const [rendered, setRendered] = useState(false);
  useEffect(() => {
    setRendered(true);
  }, []);
  useEffect(() => {}, [rendered]);

  const slideTextField = useRef(null);

  // TODO: Make buttons :active state work on mobile
  return (
    <>
      {error && <div className="error-field">{error}</div>}
      <div className="player">
        <img src={currentTrack["album_cover_url"]} alt="" />
        <div className="wrapper">
          <div className="text-field-wrapper">
            <div className="song-title">{currentTrack["title"]}</div>
            <div
              className={
                slideTextField.current?.offsetWidth <
                slideTextField.current?.scrollWidth
                  ? "song-artists slided-text"
                  : "song-artists"
              }
            >
              <span ref={slideTextField}>{currentTrack["artists"]}</span>
            </div>
          </div>
          <div className="progress-panel">
            <div className="current-s">
              {Math.floor(currentTrack["progress_s"] / 60)}:
              {currentTrack["progress_s"] % 60 < 10 && "0"}
              {parseInt(currentTrack["progress_s"] % 60)}
            </div>
            <div className="status-bar">
              <div
                className="status-bar-progress"
                style={{
                  width:
                    (100 * currentTrack["progress_s"]) /
                      currentTrack["duration_s"] +
                    "%",
                }}
              ></div>
            </div>
            <div className="song-length">
              {Math.floor(currentTrack["duration_s"] / 60)}:
              {currentTrack["duration_s"] % 60 < 10 && "0"}
              {parseInt(currentTrack["duration_s"] % 60)}
            </div>
          </div>
          <div className="control-panel">
            <button className="previous">
              <BsFillSkipStartFill />
            </button>
            <button
              className="play-pause"
              onClick={() => {
                let err = currentTrack["is_playing"]
                  ? pauseTrack()
                  : playTrack();
                err?.message && setError(err.message);
              }}
              data-testid="play-pause-button"
            >
              {currentTrack["is_playing"] ? <FaPause /> : <FaPlay />}
            </button>
            <button
              className="skip"
              onClick={() => {
                voteToSkip();
              }}
              data-votes={`${currentTrack["current-votes"]}/${votesToSkip}`}
              data-testid="skip-button"
            >
              <BsFillSkipEndFill />
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Player;
