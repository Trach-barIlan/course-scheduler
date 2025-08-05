import React from 'react';
import { render, screen } from '@testing-library/react';

describe('Minimal Test', () => {
  test('renders basic component', () => {
    const TestComponent = () => <div data-testid="test">Hello</div>;
    render(<TestComponent />);
    // Test if toBeInTheDocument is now working
    expect(screen.getByTestId('test')).toBeInTheDocument();
    expect(screen.getByTestId('test').textContent).toBe('Hello');
  });
});
