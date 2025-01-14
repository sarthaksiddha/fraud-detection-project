from typing import Dict, Any, Optional
import logging
from datetime import datetime
import kubernetes
from kubernetes import client, config
import yaml

class DeploymentManager:
    """Manage model deployment to production."""
    
    def __init__(self, k8s_config: Dict[str, Any]):
        """Initialize deployment manager.
        
        Args:
            k8s_config (Dict[str, Any]): Kubernetes configuration
        """
        self.config = k8s_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Kubernetes client
        try:
            config.load_kube_config()
            self.k8s_client = client.AppsV1Api()
            self.core_client = client.CoreV1Api()
        except Exception as e:
            self.logger.error(f"Error initializing Kubernetes client: {str(e)}")
            raise
    
    def deploy_model(self, model_version: str) -> Dict[str, Any]:
        """Deploy a specific model version to production.
        
        Args:
            model_version (str): Model version to deploy
            
        Returns:
            Dict[str, Any]: Deployment status
        """
        try:
            # Update deployment configuration
            deployment = self._get_deployment_template()
            deployment['spec']['template']['spec']['containers'][0]['env'].append({
                'name': 'MODEL_VERSION',
                'value': model_version
            })
            
            # Apply deployment
            response = self.k8s_client.patch_namespaced_deployment(
                name=self.config['deployment_name'],
                namespace=self.config['namespace'],
                body=deployment
            )
            
            return {
                'status': 'deployed',
                'model_version': model_version,
                'timestamp': datetime.utcnow(),
                'deployment_name': response.metadata.name
            }
            
        except Exception as e:
            self.logger.error(f"Error deploying model: {str(e)}")
            raise
    
    def rollback_deployment(self) -> Dict[str, Any]:
        """Rollback to previous deployment.
        
        Returns:
            Dict[str, Any]: Rollback status
        """
        try:
            # Get deployment history
            rollback = client.AppsV1beta1RollbackConfig(
                revision=0  # Rollback to previous version
            )
            
            # Execute rollback
            response = self.k8s_client.create_namespaced_deployment_rollback(
                name=self.config['deployment_name'],
                namespace=self.config['namespace'],
                body=rollback
            )
            
            return {
                'status': 'rolled_back',
                'timestamp': datetime.utcnow(),
                'deployment_name': response.metadata.name
            }
            
        except Exception as e:
            self.logger.error(f"Error rolling back deployment: {str(e)}")
            raise
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status.
        
        Returns:
            Dict[str, Any]: Deployment status
        """
        try:
            deployment = self.k8s_client.read_namespaced_deployment(
                name=self.config['deployment_name'],
                namespace=self.config['namespace']
            )
            
            return {
                'name': deployment.metadata.name,
                'replicas': deployment.status.replicas,
                'available_replicas': deployment.status.available_replicas,
                'ready_replicas': deployment.status.ready_replicas,
                'updated_replicas': deployment.status.updated_replicas,
                'conditions': [
                    {
                        'type': c.type,
                        'status': c.status,
                        'last_update': c.last_update_time
                    }
                    for c in deployment.status.conditions
                ] if deployment.status.conditions else []
            }
            
        except Exception as e:
            self.logger.error(f"Error getting deployment status: {str(e)}")
            raise
    
    def _get_deployment_template(self) -> Dict[str, Any]:
        """Get deployment template.
        
        Returns:
            Dict[str, Any]: Deployment template
        """
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': self.config['deployment_name'],
                'namespace': self.config['namespace']
            },
            'spec': {
                'replicas': self.config.get('replicas', 3),
                'selector': {
                    'matchLabels': {
                        'app': 'fraud-detection'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'fraud-detection'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'fraud-detection',
                            'image': self.config['image'],
                            'ports': [{
                                'containerPort': 8000
                            }],
                            'env': [
                                {
                                    'name': 'ENVIRONMENT',
                                    'value': self.config['environment']
                                }
                            ],
                            'resources': {
                                'requests': {
                                    'memory': '512Mi',
                                    'cpu': '250m'
                                },
                                'limits': {
                                    'memory': '1Gi',
                                    'cpu': '500m'
                                }
                            }
                        }]
                    }
                }
            }
        }