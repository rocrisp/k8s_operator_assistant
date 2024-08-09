from langchain_community.llms import Ollama

class OperatorAgent:
    def __init__(self):
        self.llm = Ollama(model="llama3:latest", verbose=True, temperature=0)
        self.services_map = {
            "configmap": self._get_configmap_code,
            "deployment": self._get_deployment_code,
            "secret": self._get_secret_code
        }

    def get_response(self, query):
        response = self.llm.invoke(query)
        return response

    def generate_operator(self, kind, services, application):
        base_code = self._generate_base_operator(kind)
        service_code = self._generate_services_code(services)
        reconciler_code = self._generate_reconciler_code(application)
        
        full_code = base_code + "\n" + service_code + "\n" + reconciler_code
        return full_code

    def _generate_base_operator(self, kind):
        base_code = f"""package main

            import (
                "context"
                "github.com/operator-framework/operator-sdk/pkg/k8sutil"
                "sigs.k8s.io/controller-runtime/pkg/manager"
                "sigs.k8s.io/controller-runtime/pkg/controller"
                "sigs.k8s.io/controller-runtime/pkg/client/config"
                "sigs.k8s.io/controller-runtime/pkg/runtime/log"
            )

            func main() {{
                mgr, err := manager.New(config.GetConfigOrDie(), manager.Options{{}})
                if err != nil {{
                    log.Log.Error(err, "unable to set up overall controller manager")
                    os.Exit(1)
                }}

                if err := controller.New("{kind}Controller", mgr, controller.Options{{Reconciler: &Reconcile{{}}}}); err != nil {{
                    log.Log.Error(err, "unable to create controller")
                    os.Exit(1)
                }}

                if err := mgr.Start(signals.SetupSignalHandler()); err != nil {{
                    log.Log.Error(err, "unable to start manager")
                    os.Exit(1)
                }}
            }}
            """
        return base_code

    def _generate_services_code(self, services):
        service_code = ""
        for service in services:
            service_code += self.services_map.get(service, lambda: "")()
        return service_code

    def _generate_reconciler_code(self, application):
        reconciler_code = f"""package main

            import (
                "context"
                "github.com/operator-framework/operator-sdk/pkg/k8sutil"
                "sigs.k8s.io/controller-runtime/pkg/reconcile"
                "sigs.k8s.io/controller-runtime/pkg/client"
                "sigs.k8s.io/controller-runtime/pkg/runtime/log"
            )

            type Reconcile struct {{
                client client.Client
            }}

            func (r *Reconcile) Reconcile(request reconcile.Request) (reconcile.Result, error) {{
                log.Log.Info("Reconciling {application}")
                // Add your application deployment logic here
                return reconcile.Result{{}}, nil
            }}
            """
        return reconciler_code

    def _get_configmap_code(self):
        return """package main

        import (
            "context"
            "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
            corev1 "k8s.io/api/core/v1"
        )

        func createConfigMap(name, namespace string, data map[string]string) *corev1.ConfigMap {{
            cm := &corev1.ConfigMap{{
                ObjectMeta: metav1.ObjectMeta{{
                    Name:      name,
                    Namespace: namespace,
                }},
                Data: data,
            }}
            return cm
        }}
        """

    def _get_deployment_code(self):
        return """package main

        import (
            appsv1 "k8s.io/api/apps/v1"
            corev1 "k8s.io/api/core/v1"
        )

        func createDeployment(name, namespace string, replicas int32) *appsv1.Deployment {{
            deploy := &appsv1.Deployment{{
                ObjectMeta: metav1.ObjectMeta{{
                    Name:      name,
                    Namespace: namespace,
                }},
                Spec: appsv1.DeploymentSpec{{
                    Replicas: &replicas,
                    Template: corev1.PodTemplateSpec{{
                        Spec: corev1.PodSpec{{
                            Containers: []corev1.Container{{
                                {{
                                    Name:  "example-container",
                                    Image: "example-image",
                                }},
                            }},
                        }},
                    }},
                }},
            }}
            return deploy
        }}
        """

    def _get_secret_code(self):
        return """package main

        import (
            corev1 "k8s.io/api/core/v1"
            metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
        )

        func createSecret(name, namespace string, data map[string][]byte) *corev1.Secret {{
            sec := &corev1.Secret{{
                ObjectMeta: metav1.ObjectMeta{{
                    Name:      name,
                    Namespace: namespace,
                }},
                Data: data,
            }}
            return sec
        }}
        """
