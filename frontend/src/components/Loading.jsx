export default function Loading({ message = 'Loading' }) {
  return (
    <div className="loading-container">
      <div className="loading-dots">
        <span /><span /><span />
      </div>
      <span style={{ fontSize: '0.75rem' }}>{message}</span>
    </div>
  )
}
