import renderer, { create } from "react-test-renderer";
import {
  fireEvent,
  getByLabelText,
  render,
  screen,
} from "@testing-library/react";
import CreateRoomForm from ".";
import { createRoom } from "../../service";
import userEvent from "@testing-library/user-event";

jest.mock("../../service");
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

describe("form does not submit when not valid", () => {
  it("when vote-to-skip is empty", async () => {
    const user = userEvent.setup();
    const { getByLabelText, getByText } = render(<CreateRoomForm />);
    await user.click(getByLabelText("Votes to skip:"));
    await user.keyboard("[Backspace]");

    await user.click(getByText("Create"));
    expect(createRoom).not.toHaveBeenCalled();
  });
});

describe("Form is submited if valid", () => {
  const defaultFormData = { votes_to_skip: "3", user_can_pause: "true" };

  test("case 1", async () => {
    const { getByText, getByLabelText } = render(<CreateRoomForm />);
    const user = userEvent.setup();

    await user.click(screen.getByText("Create"));
    expect(createRoom).toHaveBeenCalledWith(defaultFormData);
  });

  test("case 2", async () => {
    const { getByText, getByLabelText } = render(<CreateRoomForm />);
    const user = userEvent.setup();

    getByLabelText("Votes to skip:").value = "";
    await user.click(getByLabelText("Votes to skip:"));
    await user.keyboard("13");
    await user.click(getByLabelText("No control"));

    await user.click(screen.getByText("Create"));
    expect(createRoom).toHaveBeenCalledWith({
      votes_to_skip: "13",
      user_can_pause: "false",
    });
  });

  test("case 3", async () => {
    const { getByText, getByLabelText } = render(<CreateRoomForm />);
    const user = userEvent.setup();

    getByLabelText("Votes to skip:").value = "";
    await user.click(getByLabelText("Votes to skip:"));
    await user.keyboard("101");
    await user.click(getByLabelText("Can pause"));
    await user.click(screen.getByTestId("create-button"));

    expect(createRoom).toHaveBeenCalledWith({
      votes_to_skip: "101",
      user_can_pause: "true",
    });
  });
});
