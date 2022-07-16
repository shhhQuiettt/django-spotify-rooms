import { playTrack, voteToSkip, pauseTrack, getTrack } from "../../service";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Player from ".";

let mockSong = {
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

jest.mock("../../service"); //, () => {});
//   getTrack: jest.fn(() => {
//     return [mockSong, null];
//   });
//   playTrack: jest.fn();

getTrack.mockImplementation(() => {
  return [mockSong, null];
});

describe("Proper calls are made on players button", () => {
  test.todo("When song is paused, play-pause button plays");
  // test("When song is paused, play-pause button plays", async () => {
  //   const user = userEvent.setup();
  //   // const setStateMock = jest.fn()
  //   // const useStateMock = (useState) =>  [useState, setStateMock]
  //   // jest.spyOn(React, "useState").mockImplementation(useStateMock)

  //   const { getByTestId } = render(<Player />);
  //   const click = async () => {
  //     await user.click(getByTestId("play-pause-button"));
  //   };

  //   // expect(getTrack).toBeCalled();
  //   expect(playTrack).toBeCalled();
  // });
  test("When skip button is clicked voteToSkip is called", async () => {
    const user = userEvent.setup();

    const { getByTestId } = render(<Player />);
    await user.click(getByTestId("skip-button"));
    expect(voteToSkip).toHaveBeenCalled();
  });
});
