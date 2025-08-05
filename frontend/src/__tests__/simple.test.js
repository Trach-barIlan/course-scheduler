import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';

// Simple test component
const SimpleComponent = ({ text }) => {
  return <div data-testid="simple-component">{text}</div>;
};

describe('Simple Frontend Tests', () => {
  test('renders a simple component', () => {
    render(<SimpleComponent text="Hello World" />);
    expect(screen.getByTestId('simple-component')).toBeInTheDocument();
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  test('handles basic state', () => {
    const StateComponent = () => {
      const [count, setCount] = React.useState(0);
      return (
        <div>
          <span data-testid="count">{count}</span>
          <button 
            data-testid="increment" 
            onClick={() => setCount(count + 1)}
          >
            Increment
          </button>
        </div>
      );
    };

    render(<StateComponent />);
    
    expect(screen.getByTestId('count')).toHaveTextContent('0');
    
    const button = screen.getByTestId('increment');
    act(() => {
      fireEvent.click(button);
    });
    
    expect(screen.getByTestId('count')).toHaveTextContent('1');
  });

  test('handles form inputs', () => {
    const FormComponent = () => {
      const [value, setValue] = React.useState('');
      return (
        <div>
          <input
            data-testid="input"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Enter text"
          />
          <div data-testid="output">{value}</div>
        </div>
      );
    };

    render(<FormComponent />);
    
    const input = screen.getByTestId('input');
    const output = screen.getByTestId('output');
    
    expect(input).toHaveValue('');
    expect(output).toHaveTextContent('');
    
    // Simulate user input
    act(() => {
      fireEvent.change(input, { target: { value: 'test' } });
    });
    
    expect(input).toHaveValue('test');
    expect(output).toHaveTextContent('test');
  });

  test('handles conditional rendering', () => {
    const ConditionalComponent = ({ show }) => {
      return (
        <div>
          {show ? (
            <div data-testid="visible">I am visible</div>
          ) : (
            <div data-testid="hidden">I am hidden</div>
          )}
        </div>
      );
    };

    const { rerender } = render(<ConditionalComponent show={true} />);
    
    expect(screen.getByTestId('visible')).toBeInTheDocument();
    expect(screen.queryByTestId('hidden')).not.toBeInTheDocument();
    
    rerender(<ConditionalComponent show={false} />);
    
    expect(screen.queryByTestId('visible')).not.toBeInTheDocument();
    expect(screen.getByTestId('hidden')).toBeInTheDocument();
  });

  test('handles list rendering', () => {
    const ListComponent = ({ items }) => {
      return (
        <ul data-testid="list">
          {items.map((item, index) => (
            <li key={index} data-testid={`item-${index}`}>
              {item}
            </li>
          ))}
        </ul>
      );
    };

    const testItems = ['Item 1', 'Item 2', 'Item 3'];
    render(<ListComponent items={testItems} />);
    
    expect(screen.getByTestId('list')).toBeInTheDocument();
    expect(screen.getByTestId('item-0')).toHaveTextContent('Item 1');
    expect(screen.getByTestId('item-1')).toHaveTextContent('Item 2');
    expect(screen.getByTestId('item-2')).toHaveTextContent('Item 3');
  });

  test('handles accessibility', () => {
    const AccessibleComponent = () => {
      return (
        <button 
          data-testid="button"
          aria-label="Click me"
          aria-describedby="description"
        >
          Click me
        </button>
      );
    };

    render(<AccessibleComponent />);
    
    const button = screen.getByTestId('button');
    expect(button).toHaveAttribute('aria-label', 'Click me');
    expect(button).toHaveAttribute('aria-describedby', 'description');
  });

  test('handles async operations', async () => {
    const AsyncComponent = () => {
      const [data, setData] = React.useState(null);
      
      React.useEffect(() => {
        const timer = setTimeout(() => {
          setData('loaded');
        }, 100);
        
        return () => clearTimeout(timer);
      }, []);
      
      return (
        <div data-testid="async-component">
          {data ? data : 'loading...'}
        </div>
      );
    };

    render(<AsyncComponent />);
    
    expect(screen.getByTestId('async-component')).toHaveTextContent('loading...');
    
    // Wait for the async operation to complete
    await screen.findByText('loaded');
    expect(screen.getByTestId('async-component')).toHaveTextContent('loaded');
  });

  test('handles event handling', () => {
    const EventComponent = () => {
      const [clicked, setClicked] = React.useState(false);
      
      return (
        <div>
          <button 
            data-testid="event-button"
            onClick={() => setClicked(true)}
            onMouseEnter={() => setClicked(false)}
          >
            {clicked ? 'Clicked!' : 'Click me'}
          </button>
        </div>
      );
    };

    render(<EventComponent />);
    
    const button = screen.getByTestId('event-button');
    expect(button).toHaveTextContent('Click me');
    
    act(() => {
      fireEvent.click(button);
    });
    expect(button).toHaveTextContent('Clicked!');
    
    act(() => {
      fireEvent.mouseEnter(button);
    });
    expect(button).toHaveTextContent('Click me');
  });
}); 