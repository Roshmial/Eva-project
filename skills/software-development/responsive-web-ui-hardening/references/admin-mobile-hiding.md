# Admin navigation mobile hiding pattern

In Hermes Web React, the admin tab ("Управление") is intentionally hidden on mobile (≤820px) via CSS. This is a deliberate UX decision for local-first admin surfaces where mobile admin is out of scope.

## Implementation

In `services/frontend-react/src/styles.css`:

```css
@media (max-width: 820px) {
  .nav-btn-admin { display: none; }
}
```

In `services/frontend-react/src/App.jsx`, the sidebar renders navigation buttons:

```javascript
const visibleScreens = SCREENS.filter((screen) => !(screen === 'admin' && appState.user?.role !== 'admin'));
{visibleScreens.map((screen) => (
  <button key={screen} className={`nav-btn nav-btn-${screen} ...`}>
    {screen === 'chat' ? 'Чаты' : screen === 'profile' ? 'Профиль' : screen === 'jobs' ? 'Задачи' : 'Управление'}
  </button>
))}
```

The admin button gets the class `nav-btn-admin` (from `nav-btn-${screen}`), which is then hidden by the media query.

## Why this pattern

1. **Role-based filtering first**: The admin button is only rendered for `role === 'admin'` users (permission check in render logic, not just CSS).

2. **Mobile-specific hiding**: On mobile, the admin tab is hidden entirely rather than squeezed into a cramped nav bar. This follows the principle from `responsive-web-ui-hardening`: "If admin is not needed on mobile, hide the admin entry rather than squeezing it in."

3. **Desktop remains fully functional**: On desktop (>820px), the admin tab is fully visible and functional for admin users.

## When to change

If the user explicitly requests mobile admin support:
1. Remove `.nav-btn-admin { display: none; }` from the media query
2. Verify the admin screen itself is mobile-usable (tabs, tables, modals)
3. Test on iPhone portrait viewport

## Verification

- Build: `npm run react:build`
- Check the compiled CSS includes the media query rule
- On desktop: admin tab visible for admin users
- On mobile (≤820px): admin tab hidden for all users