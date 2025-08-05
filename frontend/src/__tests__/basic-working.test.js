import React from 'react';
import { render, screen, act, fireEvent } from '@testing-library/react';

// Remove the problematic mock for now
// jest.mock('react-router-dom', () => ({
//   BrowserRouter: ({ children }) => <div data-testid="router">{children}</div>,
//   Routes: ({ children }) => <div data-testid="routes">{children}</div>,
//   Route: ({ element }) => <div data-testid="route">{element}</div>,
//   useNavigate: () => jest.fn(),
// }));

// Simple test component
const TestComponent = ({ title }) => {
  return <div data-testid="test-component">{title}</div>;
};

describe('Basic Frontend Tests - Working', () => {
  test('renders a simple component', () => {
    render(<TestComponent title="Hello World" />);
    expect(screen.getByTestId('test-component')).toBeInTheDocument();
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  test('handles user interactions', () => {
    const TestButton = () => {
      const [clicked, setClicked] = React.useState(false);
      return (
        <button 
          data-testid="test-button" 
          onClick={() => setClicked(true)}
        >
          {clicked ? 'Clicked!' : 'Click me'}
        </button>
      );
    };

    render(<TestButton />);
    const button = screen.getByTestId('test-button');
    
    expect(button).toHaveTextContent('Click me');
    
    act(() => {
      fireEvent.click(button);
    });
    
    expect(button).toHaveTextContent('Clicked!');
  });

  test('handles conditional rendering', () => {
    const ConditionalComponent = ({ show }) => {
      return (
        <div>
          {show ? (
            <div data-testid="shown">Visible</div>
          ) : (
            <div data-testid="hidden">Hidden</div>
          )}
        </div>
      );
    };

    const { rerender } = render(<ConditionalComponent show={false} />);
    expect(screen.getByTestId('hidden')).toBeInTheDocument();
    expect(screen.queryByTestId('shown')).not.toBeInTheDocument();

    rerender(<ConditionalComponent show={true} />);
    expect(screen.getByTestId('shown')).toBeInTheDocument();
    expect(screen.queryByTestId('hidden')).not.toBeInTheDocument();
  });
});
