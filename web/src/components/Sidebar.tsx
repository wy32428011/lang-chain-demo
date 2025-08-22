import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { Dashboard, Analytics, Settings } from '@mui/icons-material';

const menuItems = [
  { text: '分析结果', icon: <Dashboard />, page: 'results' },
  { text: '股票分析', icon: <Analytics />, page: 'analysis' },
  { text: '设置', icon: <Settings />, page: 'settings' },
];

interface SidebarProps {
  width?: number;
  onMenuSelect?: (page: string) => void;
}

export default function Sidebar({ width = 240, onMenuSelect }: SidebarProps) {
  return (
    <Box
      sx={{
        width,
        minHeight: '100vh',
        bgcolor: 'background.paper',
        borderRight: '1px solid',
        borderColor: 'divider',
        boxShadow: 2,
      }}
    >
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => onMenuSelect?.(item.page)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
}