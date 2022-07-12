import React, { useRef, useState, useEffect } from "react";
import "./index.css";
import { FaPlay, FaPause } from "react-icons/fa";
import { BsFillSkipEndFill, BsFillSkipStartFill } from "react-icons/bs";
import { getTrack } from "../../service";

const Player = () => {
  let testData = {
    title: "Piosenka",
    duration_s: 194,
    progress_s: 23,
    album_cover_url:
      "https://freepsdflyer.com/wp-content/uploads/2021/06/Free-Spotify-Album-Cover-PSD-Template.jpg",
    is_playing: false,
    artists: "Taco hamingway, White 2115, Krzysztof Krawczyk, Fryderyk Chopin",
    // artists: "Oki",
    song_id: "123445",
  };

  const [currentTrack, setCurrentTrack] = useState(testData);

  const [error, setError] = useState(null);
  const refreshTrack = async () => {
    const [track, err] = await getTrack();
    err ? setError(err) : setCurrentTrack(track);
  };

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
              {currentTrack["progress_s"] % 60}
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
              {currentTrack["duration_s"] % 60}
            </div>
          </div>
          <div className="control-panel">
            <button className="previous">
              <BsFillSkipStartFill />
            </button>
            <button className="play-pause">
              {currentTrack["is_playing"] ? <FaPlay /> : <FaPause />}
            </button>
            <button className="skip">
              <BsFillSkipEndFill />
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Player;
