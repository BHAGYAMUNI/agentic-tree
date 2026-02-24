import React from 'react'
import { render, screen } from '@testing-library/react'
import ManualControls from '../ManualControls'

test('renders Manual Controls header', () => {
  render(<ManualControls />)
  expect(screen.getByText(/Manual Controls/i)).toBeInTheDocument()
})
