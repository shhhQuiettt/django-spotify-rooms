// Created in order to test with navigation
import { screen, render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { BrowserRouter } from "react-router-dom";

const renderWithRouter = (ui, { route = "/" } = {}) => {
  window.history.pushState({}, "Test page", route);

  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: BrowserRouter }),
  };
};

describe("When room code is not in storage", () => {
  it("Can open join-room-form", async () => {
    const { user, getByText, getByTestId } = renderWithRouter(<App />);
    await user.click(getByText("Join a room"));
    expect(getByTestId("join-room-form")).toBeInTheDocument();
  });
  it("Can open create-room-form", async () => {
    const { user, getByText, getByTestId } = renderWithRouter(<App />);

    await user.click(getByText("Create a room"));

    expect(getByTestId("create-room-form")).toBeInTheDocument();
  });
});

describe("When room code is in storage", () => {
  it("Redirects from join-room-form to room ", async () => {
    localStorage.setItem("roomCode", "123456");
    const { user, getByText, queryByTestId } = renderWithRouter(<App />);
    await user.click(getByText("Join a room"));

    expect(queryByTestId("join-room-form")).not.toBeInTheDocument();
    expect(queryByTestId("room")).toBeInTheDocument();
  });

  it("Redirects from create-room-form to room ", async () => {
    localStorage.setItem("roomCode", "123456");
    const { user, getByText, queryByTestId } = renderWithRouter(<App />);
    await user.click(getByText("Create a room"));

    expect(queryByTestId("create-room-form")).not.toBeInTheDocument();
    expect(queryByTestId("room")).toBeInTheDocument();
  });
});
