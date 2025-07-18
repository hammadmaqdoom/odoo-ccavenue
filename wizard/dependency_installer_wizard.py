from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ..tools.dependency_installer import DependencyInstaller

class DependencyInstallerWizard(models.TransientModel):
    _name = 'payment.ccavenue.dependency.installer'
    _description = 'CCAvenue Dependency Installer'

    state = fields.Selection([
        ('check', 'Check Dependencies'),
        ('install', 'Install Dependencies'),
        ('done', 'Completed')
    ], default='check')
    
    dependency_status = fields.Text('Dependency Status', readonly=True)
    installation_log = fields.Text('Installation Log', readonly=True)

    def action_check_dependencies(self):
        """Check dependency installation status"""
        status = DependencyInstaller.get_installation_status()
        
        status_text = "Dependency Status:\n\n"
        for package, info in status.items():
            icon = "✓" if info['installed'] else "✗"
            status_text += f"{icon} {package}: {'Installed' if info['installed'] else 'Missing'}\n"
            status_text += f"   {info['description']}\n\n"
        
        self.dependency_status = status_text
        
        # Check if all dependencies are installed
        all_installed = all(info['installed'] for info in status.values())
        
        if all_installed:
            self.state = 'done'
        else:
            self.state = 'install'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_install_dependencies(self):
        """Install missing dependencies"""
        results = DependencyInstaller.install_all_dependencies()
        
        log_text = "Installation Results:\n\n"
        for package, result in results.items():
            status_icon = {
                'success': '✓',
                'already_installed': '✓',
                'failed': '✗',
                'verification_failed': '⚠'
            }.get(result['status'], '?')
            
            log_text += f"{status_icon} {package}: {result['status'].replace('_', ' ').title()}\n"
            if result['message']:
                log_text += f"   {result['message']}\n"
            log_text += "\n"
        
        self.installation_log = log_text
        self.state = 'done'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }